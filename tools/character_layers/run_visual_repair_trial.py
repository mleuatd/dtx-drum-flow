#!/usr/bin/env python3
"""One-command quality-preserving visual-repair trial runner.

The runner is frame-generic: Python owns the pipeline, while frame/action/phase,
coordinates, hashes and output names live in JSON. Frame 008 is only the
regression reference and remains the only frame exercised before user approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from build_mesh_warp_pose import alpha_composite_rgba, polygon_mask, save_rgba, warp_rgba

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PREFIX = "character-assets/layers/character/"
DEFAULT_FORBIDDEN_FRAMES = ("010", "014", "028", "032")
DEFAULT_OUTPUT_NAMES = {
    "candidate": "{frameId}_mesh_v1.png",
    "review": "{frameId}_mesh_v1_review.webp",
    "compositeReview": "{frameId}_fixed_drum_v1_review.webp",
    "beforeAfterReview": "{frame}_before_after_review.webp",
    "qa": "{frame}_qa.json",
    "timing": "{frame}_timing.json",
    "runManifest": "{frame}_run_manifest.json",
    "commitManifest": "{frame}_commit_manifest.json",
    "regression": "{frame}_regression_run.json",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_path(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def path_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def repo_rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_rgba(path: Path) -> np.ndarray:
    with Image.open(path) as im:
        return np.asarray(im.convert("RGBA"))


def save_webp(array: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(array, "RGBA").save(path, format="WEBP", lossless=True, method=2)


def cache_input(path: Path, cache_dir: Path) -> tuple[Path, str, bool]:
    if not path.is_file():
        raise FileNotFoundError(path)
    digest = sha256(path)
    target = cache_dir / digest[:16] / path.name
    hit = target.exists() and sha256(target) == digest
    if not hit:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        if sha256(target) != digest:
            raise RuntimeError(f"cache copy SHA mismatch: {path}")
    return target, digest, hit


def output_names(cfg: dict) -> dict[str, str]:
    frame_id = str(cfg["frameId"])
    frame = frame_id.split("_", 1)[0]
    values = dict(DEFAULT_OUTPUT_NAMES)
    values.update(cfg.get("outputNames", {}))
    return {k: str(v).format(frameId=frame_id, frame=frame) for k, v in values.items()}


def validate_config(cfg: dict) -> None:
    required = [
        "schemaVersion", "frameId", "actionKey", "phase", "inputPng",
        "fixedDrumPng", "roi", "deformationPolygon",
        "fixedRects", "sourcePoints", "targetPoints", "landmarks",
        "pedalTolerancePx", "brokenSourceSha256",
        "fixedDrumSha256", "runtimeWritable", "userApprovalStatus",
        "visualQaRequired",
    ]
    transplant_mode = "basePng" in cfg or "warpSourcePng" in cfg
    required += (
        ["basePng", "warpSourcePng", "baseSha256", "warpSourceSha256"]
        if transplant_mode
        else ["normalSourcePng", "normalSourceSha256"]
    )
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError("missing config fields: " + ", ".join(missing))
    if cfg.get("visualQaRequired") is not True:
        raise ValueError("visualQaRequired must be true")
    if cfg.get("runtimeWritable") is not False:
        raise ValueError("trial runner requires runtimeWritable=false")
    if len(cfg["sourcePoints"]) != len(cfg["targetPoints"]):
        raise ValueError("sourcePoints/targetPoints length mismatch")
    if len(cfg["sourcePoints"]) < 3:
        raise ValueError("at least 3 source/target points are required")
    for name in ("hip", "knee", "ankle", "toe", "pedalEndpoint", "pedalTarget"):
        pt = cfg["landmarks"].get(name)
        if not (isinstance(pt, list) and len(pt) == 2):
            raise ValueError(f"invalid landmark: {name}")
    roi = cfg["roi"]
    if not all(k in roi for k in ("x1", "y1", "x2", "y2")):
        raise ValueError("roi requires x1/y1/x2/y2")


def fixed_mask(shape: tuple[int, int], rects: list[dict]) -> np.ndarray:
    h, w = shape
    mask = np.zeros((h, w), dtype=bool)
    for r in rects:
        x1, y1, x2, y2 = (int(r[k]) for k in ("x1", "y1", "x2", "y2"))
        mask[max(0, y1):min(h, y2), max(0, x1):min(w, x2)] = True
    return mask


def run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def guarded_commit(paths: list[Path], expected_main_sha: str, message: str,
                   forbidden_tokens: tuple[str, ...]) -> tuple[str, float, float]:
    prep = time.perf_counter()
    origin_main = run_git("rev-parse", "origin/main")
    if origin_main != expected_main_sha:
        raise RuntimeError(f"origin/main moved: {expected_main_sha} -> {origin_main}")
    rels = [repo_rel(p) for p in paths]
    for p in rels:
        if p.startswith(RUNTIME_PREFIX):
            raise RuntimeError(f"runtime path blocked: {p}")
        if any(tok in p for tok in forbidden_tokens):
            raise RuntimeError(f"other frame path blocked: {p}")
    subprocess.check_call(["git", "add", "--", *rels], cwd=ROOT)
    staged = run_git("diff", "--cached", "--name-only").splitlines()
    if any(p.startswith(RUNTIME_PREFIX) for p in staged):
        raise RuntimeError("runtime PNG detected in staged files")
    if any(any(tok in p for tok in forbidden_tokens) for p in staged):
        raise RuntimeError("blocked other-frame file detected in staged files")
    prep_seconds = time.perf_counter() - prep
    reg = time.perf_counter()
    subprocess.check_call(["git", "commit", "-m", message], cwd=ROOT)
    commit_sha = run_git("rev-parse", "HEAD")
    return commit_sha, prep_seconds, time.perf_counter() - reg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-config", required=True, type=Path)
    ap.add_argument("--source", type=Path)
    ap.add_argument("--broken-source", type=Path)
    ap.add_argument("--fixed-drum", type=Path)
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--cache-dir", type=Path, default=Path(".cache/visual-repair"))
    ap.add_argument("--png-compress-level", type=int, default=1, choices=range(10))
    ap.add_argument("--git-commit", action="store_true")
    ap.add_argument("--start-main-sha")
    ap.add_argument("--commit-message", default="tooling: automated visual repair trial")
    args = ap.parse_args()

    total_start = time.perf_counter()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    start_main_sha = args.start_main_sha
    if start_main_sha is None and (ROOT / ".git").exists():
        start_main_sha = run_git("rev-parse", "HEAD")

    stage = time.perf_counter()
    cfg_path = repo_path(args.frame_config)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    validate_config(cfg)
    config_sha = sha256(cfg_path)
    names = output_names(cfg)
    config_validation_seconds = time.perf_counter() - stage

    transplant_mode = "basePng" in cfg or "warpSourcePng" in cfg
    source = repo_path(args.source or (cfg["warpSourcePng"] if transplant_mode else cfg["normalSourcePng"]))
    base = repo_path(cfg["basePng"]) if transplant_mode else source
    broken = repo_path(args.broken_source or cfg["inputPng"])
    drum = repo_path(args.fixed_drum or cfg["fixedDrumPng"])
    out_dir = repo_path(args.output_dir or cfg.get("outputDir") or cfg_path.parent)
    cache_dir = repo_path(args.cache_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stage = time.perf_counter()
    source_c, source_sha, source_hit = cache_input(source, cache_dir)
    if transplant_mode and base.resolve() != source.resolve():
        base_c, base_sha, base_hit = cache_input(base, cache_dir)
    else:
        base_c, base_sha, base_hit = source_c, source_sha, source_hit
    broken_c, broken_sha, broken_hit = cache_input(broken, cache_dir)
    drum_c, drum_sha, drum_hit = cache_input(drum, cache_dir)
    cache_seconds = time.perf_counter() - stage

    expected = {
        ("warpSourceSha256" if transplant_mode else "normalSourceSha256"): source_sha,
        "brokenSourceSha256": broken_sha,
        "fixedDrumSha256": drum_sha,
    }
    if transplant_mode:
        expected["baseSha256"] = base_sha
    for key, actual in expected.items():
        wanted = cfg.get(key)
        if wanted not in (None, "", "AUTO") and wanted != actual:
            raise RuntimeError(f"{key} mismatch: {actual} != {wanted}")

    timings = {
        "configValidationSeconds": round(config_validation_seconds, 6),
        "cacheCheckAndHashSeconds": round(cache_seconds, 6),
        "gitCommitPreparationSeconds": None,
        "gitRegistrationSeconds": None,
    }

    stage = time.perf_counter()
    source_rgba = load_rgba(source_c)
    base_rgba = load_rgba(base_c) if transplant_mode else source_rgba
    broken_rgba = load_rgba(broken_c)
    drum_rgba = load_rgba(drum_c)
    timings["loadSeconds"] = round(time.perf_counter() - stage, 6)

    stage = time.perf_counter()
    warped, allowed = warp_rgba(source_rgba, cfg)
    if transplant_mode:
        candidate = base_rgba.copy()
        candidate[allowed] = warped[allowed]
    else:
        candidate = warped
    secondary_allowed = np.zeros(candidate.shape[:2], dtype=bool)
    for repair in cfg.get("secondaryRepairRegions", []):
        if repair.get("operation") != "clear":
            raise ValueError(f"unsupported secondary repair operation: {repair.get('operation')}")
        clear = polygon_mask((candidate.shape[1], candidate.shape[0]), repair["polygon"])
        candidate[clear] = 0
        secondary_allowed |= clear
        allowed |= clear
    timings["warpSeconds"] = round(time.perf_counter() - stage, 6)

    candidate_path = out_dir / names["candidate"]
    stage = time.perf_counter()
    save_rgba(candidate, candidate_path, args.png_compress_level)
    timings["candidateSaveSeconds"] = round(time.perf_counter() - stage, 6)

    stage = time.perf_counter()
    diff = np.any(candidate != base_rgba, axis=2)
    outside = diff & ~allowed
    fmask = fixed_mask(base_rgba.shape[:2], cfg["fixedRects"])
    fmask &= ~secondary_allowed
    fixed_changed = diff & fmask
    ys, xs = np.nonzero(diff)
    bbox = None if not xs.size else {
        "x": int(xs.min()), "y": int(ys.min()),
        "width": int(xs.max() - xs.min() + 1),
        "height": int(ys.max() - ys.min() + 1),
    }
    endpoint = np.asarray(cfg["landmarks"]["pedalEndpoint"], dtype=float)
    pedal = np.asarray(cfg["landmarks"]["pedalTarget"], dtype=float)
    distance = float(np.linalg.norm(endpoint - pedal))
    tolerance = float(cfg["pedalTolerancePx"])
    candidate_sha = sha256(candidate_path)
    checks = {
        "canvas1448x1086": candidate.shape[:2] == (1086, 1448),
        "rgba": candidate.shape[2] == 4,
        "alphaChannelPresent": candidate.shape[2] == 4,
        "sourceShaMatchesConfig": cfg.get(
            "warpSourceSha256" if transplant_mode else "normalSourceSha256"
        ) in (None, "", "AUTO", source_sha),
        "baseShaMatchesConfig": (
            cfg.get("baseSha256") in (None, "", "AUTO", base_sha)
            if transplant_mode else True
        ),
        "brokenSourceShaMatchesConfig": cfg.get("brokenSourceSha256") in (None, "", "AUTO", broken_sha),
        "fixedDrumShaMatchesConfig": cfg.get("fixedDrumSha256") in (None, "", "AUTO", drum_sha),
        "candidateDiffersFromSource": int(np.count_nonzero(diff)) > 0,
        "outsideAllowedZero": int(np.count_nonzero(outside)) == 0,
        "fixedRegionsZero": int(np.count_nonzero(fixed_changed)) == 0,
        "pedalContactWithinTolerance": distance <= tolerance,
        "runtimeWritableFalse": cfg.get("runtimeWritable") is False,
        "visualQaRequiredTrue": cfg.get("visualQaRequired") is True,
        "userApprovalPending": str(cfg.get("userApprovalStatus", "")).upper() != "APPROVED",
    }
    qa = {
        "schemaVersion": 4,
        "frameId": cfg["frameId"],
        "actionKey": cfg["actionKey"],
        "phase": cfg["phase"],
        "source": path_label(source), "sourceSha256": source_sha,
        "warpSource": path_label(source) if transplant_mode else None,
        "warpSourceSha256": source_sha if transplant_mode else None,
        "base": path_label(base), "baseSha256": base_sha,
        "brokenSource": path_label(broken), "brokenSourceSha256": broken_sha,
        "fixedDrum": path_label(drum), "fixedDrumSha256": drum_sha,
        "config": path_label(cfg_path), "configSha256": config_sha,
        "candidate": path_label(candidate_path), "candidateSha256": candidate_sha,
        "canvas": [int(candidate.shape[1]), int(candidate.shape[0])],
        "mode": "RGBA",
        "alphaChannelPresent": candidate.shape[2] == 4,
        "changedPixels": int(np.count_nonzero(diff)),
        "outsideAllowedChangedPixels": int(np.count_nonzero(outside)),
        "fixedRegionChangedPixels": int(np.count_nonzero(fixed_changed)),
        "changedBBox": bbox,
        "pedalEndpoint": endpoint.tolist(),
        "pedalTarget": pedal.tolist(),
        "pedalDistancePx": round(distance, 3),
        "pedalTolerancePx": tolerance,
        "visualQaRequired": True,
        "checks": checks,
    }
    exp = cfg.get("expectedRegression", {})
    qa["regressionChecks"] = {
        "changedPixelsMatch": qa["changedPixels"] == exp.get("changedPixels", qa["changedPixels"]),
        "changedBBoxMatch": qa["changedBBox"] == exp.get("changedBBox", qa["changedBBox"]),
        "outsideAllowedMatch": qa["outsideAllowedChangedPixels"] == exp.get("outsideAllowedChangedPixels", 0),
        "pedalDistanceMatch": abs(
            qa["pedalDistancePx"] - float(exp.get("pedalDistancePx", qa["pedalDistancePx"]))
        ) <= 0.01,
    } if exp else {}
    qa["machinePass"] = all(checks.values()) and all(qa["regressionChecks"].values())
    timings["qaSeconds"] = round(time.perf_counter() - stage, 6)

    stage = time.perf_counter()
    composite = alpha_composite_rgba(drum_rgba, candidate)
    composite_review = out_dir / names["compositeReview"]
    save_webp(composite, composite_review)
    timings["fixedDrumCompositeSeconds"] = round(time.perf_counter() - stage, 6)

    stage = time.perf_counter()
    review_path = out_dir / names["review"]
    save_webp(candidate, review_path)
    timings["reviewGenerationSeconds"] = round(time.perf_counter() - stage, 6)

    stage = time.perf_counter()
    gap = np.zeros((8, candidate.shape[1], 4), dtype=np.uint8)
    gap[:, :, 3] = 255
    before_after = np.concatenate([broken_rgba, gap, candidate], axis=0)
    before_after_path = out_dir / names["beforeAfterReview"]
    save_webp(before_after, before_after_path)
    timings["beforeAfterGenerationSeconds"] = round(time.perf_counter() - stage, 6)

    qa_path = out_dir / names["qa"]
    timing_path = out_dir / names["timing"]
    manifest_path = out_dir / names["runManifest"]
    commit_manifest_path = out_dir / names["commitManifest"]
    regression_path = out_dir / names["regression"]

    timings["candidateToReviewCompleteSeconds"] = round(
        timings["warpSeconds"] + timings["candidateSaveSeconds"] + timings["qaSeconds"] +
        timings["fixedDrumCompositeSeconds"] + timings["reviewGenerationSeconds"] +
        timings["beforeAfterGenerationSeconds"], 6
    )

    stage = time.perf_counter()
    generated_data_paths = [candidate_path, review_path, composite_review, before_after_path]
    forbidden = tuple(str(x) for x in cfg.get("forbiddenFrameTokens", DEFAULT_FORBIDDEN_FRAMES))
    eligible = generated_data_paths + [qa_path, timing_path, manifest_path, commit_manifest_path, regression_path, cfg_path]
    eligible_labels = [path_label(p) for p in eligible]
    safety = {
        "runtimePathsIncluded": [p for p in eligible_labels if p.startswith(RUNTIME_PREFIX)],
        "otherFramePathsIncluded": [p for p in eligible_labels if any(tok in p for tok in forbidden)],
    }
    excluded = []
    if not qa["machinePass"]:
        excluded.extend(path_label(p) for p in generated_data_paths)
    end_main_sha = run_git("rev-parse", "HEAD") if (ROOT / ".git").exists() else None
    run_manifest = {
        "schemaVersion": 3,
        "runId": run_id,
        "frame": str(cfg["frameId"]).split("_", 1)[0],
        "frameId": cfg["frameId"],
        "actionKey": cfg["actionKey"],
        "phase": cfg["phase"],
        "startMainSha": start_main_sha,
        "endMainShaCheck": end_main_sha,
        "inputs": {
            "normalSource": (
                None if transplant_mode else
                {"path": path_label(source), "sha256": source_sha, "cacheHit": source_hit}
            ),
            "warpSource": (
                {"path": path_label(source), "sha256": source_sha, "cacheHit": source_hit}
                if transplant_mode else None
            ),
            "base": {"path": path_label(base), "sha256": base_sha, "cacheHit": base_hit},
            "brokenSource": {"path": path_label(broken), "sha256": broken_sha, "cacheHit": broken_hit},
            "fixedDrum": {"path": path_label(drum), "sha256": drum_sha, "cacheHit": drum_hit},
            "config": {"path": path_label(cfg_path), "sha256": config_sha},
        },
        "generatedFiles": [path_label(p) for p in generated_data_paths],
        "filesEligibleForCommit": eligible_labels if qa["machinePass"] else [
            path_label(p) for p in (qa_path, timing_path, manifest_path, commit_manifest_path, regression_path, cfg_path)
        ],
        "filesExcludedFromCommit": excluded,
        "runtimeChanged": False,
        "otherFramesTouched": False,
        "visualQaRequired": True,
        "userApproved": str(cfg.get("userApprovalStatus", "")).upper() == "APPROVED",
        "machinePass": qa["machinePass"],
    }
    commit_manifest = {
        "schemaVersion": 3,
        "machinePass": qa["machinePass"],
        "eligibleForCandidateCommit": (
            qa["machinePass"] and not safety["runtimePathsIncluded"] and not safety["otherFramePathsIncluded"]
        ),
        "filesEligibleForCommit": run_manifest["filesEligibleForCommit"],
        "filesExcludedFromCommit": run_manifest["filesExcludedFromCommit"],
        "safety": safety,
    }
    timings["manifestGenerationSeconds"] = round(time.perf_counter() - stage, 6)
    timings["totalLocalPipelineSeconds"] = round(time.perf_counter() - total_start, 6)

    qa["timings"] = timings
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    timing_path.write_text(
        json.dumps({"schemaVersion": 4, "stages": timings}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    output_records = []
    for p in generated_data_paths + [qa_path, timing_path]:
        output_records.append({"path": path_label(p), "sha256": sha256(p)})
    run_manifest["outputs"] = output_records
    manifest_path.write_text(json.dumps(run_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    commit_manifest_path.write_text(
        json.dumps(commit_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    regression = {
        "schemaVersion": 2,
        "frame": run_manifest["frame"],
        "frameId": cfg["frameId"],
        "machinePass": qa["machinePass"],
        "visualQaRequired": True,
        "userApprovalStatus": cfg.get("userApprovalStatus"),
        "runtimeModified": False,
        "otherFramesTouched": False,
        "changedPixels": qa["changedPixels"],
        "changedBBox": qa["changedBBox"],
        "outsideAllowedChangedPixels": qa["outsideAllowedChangedPixels"],
        "fixedRegionChangedPixels": qa["fixedRegionChangedPixels"],
        "pedalDistancePx": qa["pedalDistancePx"],
        "candidateCanvas": qa["canvas"],
        "candidateMode": qa["mode"],
        "timings": timings,
        "candidateSha256": candidate_sha,
        "sourceSha256": source_sha,
        "warpSourceSha256": source_sha if transplant_mode else None,
        "baseSha256": base_sha,
        "brokenSourceSha256": broken_sha,
        "fixedDrumSha256": drum_sha,
        "configSha256": config_sha,
    }
    regression_path.write_text(json.dumps(regression, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.git_commit:
        if not commit_manifest["eligibleForCandidateCommit"]:
            raise RuntimeError("candidate commit blocked by QA/safety")
        if not args.start_main_sha:
            raise RuntimeError("--start-main-sha required with --git-commit")
        commit_paths = generated_data_paths + [
            qa_path, timing_path, manifest_path, commit_manifest_path, regression_path, cfg_path
        ]
        commit_sha, prep_s, reg_s = guarded_commit(
            commit_paths, args.start_main_sha, args.commit_message, forbidden
        )
        print(json.dumps({
            "machinePass": True,
            "commitSha": commit_sha,
            "gitCommitPreparationSeconds": round(prep_s, 6),
            "gitRegistrationSeconds": round(reg_s, 6),
            "timings": timings,
        }, ensure_ascii=False))
    else:
        print(json.dumps({
            "machinePass": qa["machinePass"],
            "commitEligible": commit_manifest["eligibleForCandidateCommit"],
            "timings": timings,
        }, ensure_ascii=False))
    return 0 if qa["machinePass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
