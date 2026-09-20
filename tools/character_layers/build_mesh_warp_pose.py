#!/usr/bin/env python3
"""Build one topology-preserving character pose from a JSON warp config.

The PNG writer defaults to a fast *lossless* compression level. This changes
file size/compression work only; decoded RGBA pixels are identical.
"""

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
    with Image.open(path) as image:
        return np.asarray(image.convert("RGBA"))


def save_rgba(array: np.ndarray, path: Path, compress_level: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(array, "RGBA").save(path, format="PNG", compress_level=compress_level)


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


def alpha_composite_rgba(bottom: np.ndarray, top: np.ndarray) -> np.ndarray:
    if bottom.shape != top.shape:
        raise ValueError(f"composite size mismatch: {bottom.shape} != {top.shape}")
    b = bottom.astype(np.float32) / 255.0
    t = top.astype(np.float32) / 255.0
    ta = t[:, :, 3:4]
    ba = b[:, :, 3:4]
    out_a = ta + ba * (1.0 - ta)
    out_rgb_premul = t[:, :, :3] * ta + b[:, :, :3] * ba * (1.0 - ta)
    out_rgb = np.divide(
        out_rgb_premul,
        out_a,
        out=np.zeros_like(out_rgb_premul),
        where=out_a > 0,
    )
    out = np.concatenate([out_rgb, out_a], axis=2)
    return np.clip(np.rint(out * 255.0), 0, 255).astype(np.uint8)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fixed-drum", type=Path)
    parser.add_argument("--preview-output", type=Path)
    parser.add_argument("--qa-output", required=True, type=Path)
    parser.add_argument("--timing-output", required=True, type=Path)
    parser.add_argument(
        "--png-compress-level",
        type=int,
        default=1,
        choices=range(0, 10),
        metavar="0..9",
        help="Lossless PNG compression level. 1 is the speed-oriented standard.",
    )
    args = parser.parse_args()

    timings: dict[str, float] = {}
    started = time.perf_counter()

    stage = time.perf_counter()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    source = load_rgba(args.source)
    timings["loadSeconds"] = round(time.perf_counter() - stage, 6)

    stage = time.perf_counter()
    result, allowed = warp_rgba(source, config)
    timings["warpSeconds"] = round(time.perf_counter() - stage, 6)

    stage = time.perf_counter()
    save_rgba(result, args.output, args.png_compress_level)
    timings["saveCandidateSeconds"] = round(time.perf_counter() - stage, 6)

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
        "schemaVersion": 2,
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
        "pngCompressLevel": args.png_compress_level,
        "checks": {
            "canvas1448x1086": source.shape[:2] == (1086, 1448),
            "outsideAllowedZero": int(np.count_nonzero(outside)) == 0,
            "changedVisible": int(np.count_nonzero(diff)) > 0,
            "pedalContactWithinTolerance": pedal_distance <= tolerance,
        },
        "visualQaRequired": True,
    }
    qa["machinePass"] = all(qa["checks"].values())
    args.qa_output.parent.mkdir(parents=True, exist_ok=True)
    args.qa_output.write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    timings["qaSeconds"] = round(time.perf_counter() - stage, 6)

    if args.fixed_drum and args.preview_output:
        stage = time.perf_counter()
        drum = load_rgba(args.fixed_drum)
        preview = alpha_composite_rgba(drum, result)
        save_rgba(preview, args.preview_output, args.png_compress_level)
        timings["fixedDrumCompositeSeconds"] = round(time.perf_counter() - stage, 6)

    timings["totalSeconds"] = round(time.perf_counter() - started, 6)
    args.timing_output.parent.mkdir(parents=True, exist_ok=True)
    args.timing_output.write_text(
        json.dumps(
            {
                "schemaVersion": 2,
                "pngCompression": {
                    "format": "PNG",
                    "lossless": True,
                    "compressLevel": args.png_compress_level,
                },
                "stages": timings,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"machinePass": qa["machinePass"], "timings": timings}, ensure_ascii=False))


if __name__ == "__main__":
    main()
