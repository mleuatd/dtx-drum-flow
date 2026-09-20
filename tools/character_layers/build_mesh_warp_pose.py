#!/usr/bin/env python3
"""Build one topology-preserving character pose from a JSON warp config."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"))


def polygon_mask(size: tuple[int, int], points: list[list[float]]) -> np.ndarray:
    image = Image.new("L", size, 0)
    ImageDraw.Draw(image).polygon([tuple(p) for p in points], fill=255)
    return np.asarray(image) > 0


def warp_rgba(source: np.ndarray, config: dict) -> tuple[np.ndarray, np.ndarray]:
    height, width = source.shape[:2]
    src_points = np.asarray(config["sourcePoints"], dtype=np.float64)
    dst_points = np.asarray(config["targetPoints"], dtype=np.float64)
    if src_points.shape != dst_points.shape or src_points.shape[1] != 2:
        raise ValueError("sourcePoints and targetPoints must be matching Nx2 arrays")

    # Inverse mapping: each destination pixel asks where to sample the source.
    inverse = RBFInterpolator(
        dst_points,
        src_points,
        kernel="thin_plate_spline",
        smoothing=float(config.get("smoothing", 0.0)),
    )
    roi = config["roi"]
    x1, y1, x2, y2 = [int(roi[k]) for k in ("x1", "y1", "x2", "y2")]
    yy, xx = np.mgrid[y1:y2, x1:x2]
    query = np.column_stack([xx.ravel(), yy.ravel()])
    sample = inverse(query)
    sample_x = sample[:, 0].reshape(yy.shape)
    sample_y = sample[:, 1].reshape(yy.shape)

    warped_roi = np.empty((y2 - y1, x2 - x1, 4), dtype=np.uint8)
    for channel in range(4):
        values = map_coordinates(
            source[:, :, channel],
            [sample_y, sample_x],
            order=1,
            mode="constant",
            cval=0,
            prefilter=False,
        )
        warped_roi[:, :, channel] = np.clip(np.rint(values), 0, 255).astype(np.uint8)

    allowed = polygon_mask((width, height), config["deformationPolygon"])
    fixed = np.zeros((height, width), dtype=bool)
    for rect in config.get("fixedRects", []):
        rx1, ry1, rx2, ry2 = [int(rect[k]) for k in ("x1", "y1", "x2", "y2")]
        fixed[ry1:ry2, rx1:rx2] = True
    allowed &= ~fixed

    result = source.copy()
    local_allowed = allowed[y1:y2, x1:x2]
    result_roi = result[y1:y2, x1:x2]
    result_roi[local_allowed] = warped_roi[local_allowed]
    result[y1:y2, x1:x2] = result_roi
    return result, allowed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fixed-drum", type=Path)
    parser.add_argument("--preview-output", type=Path)
    parser.add_argument("--qa-output", required=True, type=Path)
    parser.add_argument("--timing-output", required=True, type=Path)
    args = parser.parse_args()

    timings: dict[str, float] = {}
    started = time.perf_counter()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    source = load_rgba(args.source)
    timings["loadSeconds"] = round(time.perf_counter() - started, 6)

    stage = time.perf_counter()
    result, allowed = warp_rgba(source, config)
    timings["warpSeconds"] = round(time.perf_counter() - stage, 6)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result, "RGBA").save(args.output, optimize=True)
    timings["saveCandidateSeconds"] = round(time.perf_counter() - stage - timings["warpSeconds"], 6)

    stage = time.perf_counter()
    diff = np.any(result != source, axis=2)
    outside = diff & ~allowed
    changed_y, changed_x = np.nonzero(diff)
    bbox = None
    if changed_x.size:
        bbox = {
            "x": int(changed_x.min()),
            "y": int(changed_y.min()),
            "width": int(changed_x.max() - changed_x.min() + 1),
            "height": int(changed_y.max() - changed_y.min() + 1),
        }

    endpoint = np.asarray(config["targetPoints"][-1], dtype=float)
    pedal = np.asarray(config["pedalTarget"], dtype=float)
    pedal_distance = float(np.linalg.norm(endpoint - pedal))
    tolerance = float(config["pedalTolerancePx"])
    qa = {
        "schemaVersion": 1,
        "source": str(args.source),
        "sourceSha256": sha256(args.source),
        "candidate": str(args.output),
        "candidateSha256": sha256(args.output),
        "canvas": [int(source.shape[1]), int(source.shape[0])],
        "mode": "RGBA",
        "changedPixels": int(np.count_nonzero(diff)),
        "outsideAllowedChangedPixels": int(np.count_nonzero(outside)),
        "changedBBox": bbox,
        "pedalEndpoint": endpoint.tolist(),
        "pedalTarget": pedal.tolist(),
        "pedalDistancePx": round(pedal_distance, 3),
        "pedalTolerancePx": tolerance,
        "checks": {
            "canvas1448x1086": source.shape[:2] == (1086, 1448),
            "outsideAllowedZero": int(np.count_nonzero(outside)) == 0,
            "changedVisible": int(np.count_nonzero(diff)) > 0,
            "pedalContactWithinTolerance": pedal_distance <= tolerance,
        },
        "visualQaRequired": True,
    }
    qa["machinePass"] = all(qa["checks"].values())
    args.qa_output.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    timings["qaSeconds"] = round(time.perf_counter() - stage, 6)

    if args.fixed_drum and args.preview_output:
        stage = time.perf_counter()
        drum = Image.open(args.fixed_drum).convert("RGBA")
        candidate = Image.open(args.output).convert("RGBA")
        Image.alpha_composite(drum, candidate).save(args.preview_output, optimize=True)
        timings["fixedDrumCompositeSeconds"] = round(time.perf_counter() - stage, 6)

    timings["totalSeconds"] = round(time.perf_counter() - started, 6)
    args.timing_output.write_text(
        json.dumps({"schemaVersion": 1, "stages": timings}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"machinePass": qa["machinePass"], "timings": timings}, ensure_ascii=False))


if __name__ == "__main__":
    main()
