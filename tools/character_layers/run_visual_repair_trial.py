#!/usr/bin/env python3
"""One-command, quality-preserving visual-repair trial runner.

Frame 008 is the regression reference. The tool keeps runtime assets read-only,
caches immutable inputs by SHA-256, validates config, runs the existing mesh warp,
performs machine QA, emits review-only images separately, records timings, and
optionally creates a guarded git commit after PASS.
"""
from __future__ import annotations

import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image

from build_mesh_warp_pose import warp_rgba, alpha_composite_rgba, save_rgba

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_FRAME_TOKENS = ("010", "014", "028", "032")
RUNTIME_PREFIX = "character-assets/layers/character/"
GENERATED_NAMES = {
    "candidate": "008_bd_rf_hit_mesh_v1.png",
    "review": "008_bd_rf_hit_mesh_v1_review.webp",
    "compositeReview": "008_bd_rf_hit_fixed_drum_v1_review.webp",
    "beforeAfterReview": "008_before_after_review.webp",
    "qa": "008_qa.json",
    "timing": "008_timing.json",
    "runManifest": "008_run_manifest.json",
    "commitManifest": "008_commit_manifest.json",
    "regression": "008_regression_run.json",
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

def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()

def load_rgba(path: Path) -> np.ndarray:
    with Image.open(path) as im:
        return np.asarray(im.convert("RGBA"))

def cache_input(path: Path, cache_dir: Path) -> tuple[Path, str, bool]:
    digest = sha256(path)
    target = cache_dir / digest[:16] / path.name
    hit = target.exists() and sha256(target) == digest
    if not hit:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        if sha256(target) != digest:
            raise RuntimeError(f"cache copy SHA mismatch: {path}")
    return target, digest, hit

def validate_config(cfg: dict) -> None:
    required = [
        "actionKey","phase","roi","sourcePoints","targetPoints","deformationPolygon",
        "fixedRects","pedalTarget","pedalTolerancePx","inputPng","normalSourcePng",
        "fixedDrumPng","normalSourceSha256","fixedDrumSha256","runtimeWritable",
        "userApprovalStatus","landmarks"
    ]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError("missing config fields: " + ", ".join(missing))
    if cfg["actionKey"] != "BD:RF" or cfg["phase"] != "hit":
        raise ValueError("008 regression accepts only BD:RF hit")
    if cfg.get("runtimeWritable") is not False:
        raise ValueError("runtimeWritable must remain false before user approval")
    if len(cfg["sourcePoints"]) != len(cfg["targetPoints"]):
        raise ValueError("sourcePoints/targetPoints length mismatch")
    for name in ("hip","knee","ankle","toe","pedalEndpoint","pedalTarget"):
        pt = cfg["landmarks"].get(name)
        if not (isinstance(pt, list) and len(pt) == 2):
            raise ValueError(f"invalid landmark: {name}")

def fixed_mask(shape: tuple[int,int], rects: list[dict]) -> np.ndarray:
    h,w = shape
    mask = np.zeros((h,w), dtype=bool)
    for r in rects:
        x1,y1,x2,y2 = (int(r[k]) for k in ("x1","y1","x2","y2"))
        mask[max(0,y1):min(h,y2), max(0,x1):min(w,x2)] = True
    return mask

def save_webp(array: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(array, "RGBA").save(path, format="WEBP", lossless=True, method=2)

def run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def guarded_commit(paths: list[Path], expected_main_sha: str, message: str) -> str:
    origin_main = run_git("rev-parse", "origin/main")
    if origin_main != expected_main_sha:
        raise RuntimeError(f"origin/main moved: {expected_main_sha} -> {origin_main}")
    rels = [rel(p) for p in paths]
    for p in rels:
        if p.startswith(RUNTIME_PREFIX):
            raise RuntimeError(f"runtime path blocked: {p}")
        if any(tok in Path(p).name for tok in FORBIDDEN_FRAME_TOKENS):
            raise RuntimeError(f"other frame path blocked: {p}")
    subprocess.check_call(["git","add","--",*rels], cwd=ROOT)
    staged = run_git("diff","--cached","--name-only").splitlines()
    if any(p.startswith(RUNTIME_PREFIX) for p in staged):
        raise RuntimeError("runtime PNG detected in staged files")
    if any(any(tok in Path(p).name for tok in FORBIDDEN_FRAME_TOKENS) for p in staged):
        raise RuntimeError("010/014/028/032 file detected in staged files")
    subprocess.check_call(["git","commit","-m",message], cwd=ROOT)
    return run_git("rev-parse","HEAD")

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
    ap.add_argument("--commit-message", default="tooling: automate fast quality-preserving visual repair trials")
    args = ap.parse_args()

    total_start = time.perf_counter()
    cfg_path = repo_path(args.frame_config)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    validate_config(cfg)
    config_sha = sha256(cfg_path)

    source = repo_path(args.source or cfg["normalSourcePng"])
    broken = repo_path(args.broken_source or cfg["inputPng"])
    drum = repo_path(args.fixed_drum or cfg["fixedDrumPng"])
    out_dir = repo_path(args.output_dir or cfg.get("outputDir") or cfg_path.parent)
    cache_dir = repo_path(args.cache_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stage = time.perf_counter()
    source_c, source_sha, source_hit = cache_input(source, cache_dir)
    broken_c, broken_sha, broken_hit = cache_input(broken, cache_dir)
    drum_c, drum_sha, drum_hit = cache_input(drum, cache_dir)
    cache_seconds = time.perf_counter() - stage

    expected_source = cfg.get("normalSourceSha256")
    if expected_source not in (None,"","AUTO") and source_sha != expected_source:
        raise RuntimeError(f"normal source SHA mismatch: {source_sha} != {expected_source}")
    expected_drum = cfg.get("fixedDrumSha256")
    if expected_drum not in (None,"","AUTO") and drum_sha != expected_drum:
        raise RuntimeError(f"fixed drum SHA mismatch: {drum_sha} != {expected_drum}")
    expected_broken = cfg.get("brokenSourceSha256")
    if expected_broken not in (None,"","AUTO") and broken_sha != expected_broken:
        raise RuntimeError(f"broken source SHA mismatch: {broken_sha} != {expected_broken}")

    timings = {"cacheAndHashSeconds": round(cache_seconds,6)}
    stage = time.perf_counter()
    source_rgba = load_rgba(source_c)
    broken_rgba = load_rgba(broken_c)
    drum_rgba = load_rgba(drum_c)
    timings["loadCachedInputsSeconds"] = round(time.perf_counter()-stage,6)

    stage = time.perf_counter()
    candidate, allowed = warp_rgba(source_rgba, cfg)
    timings["warpSeconds"] = round(time.perf_counter()-stage,6)

    candidate_path = out_dir / GENERATED_NAMES["candidate"]
    stage = time.perf_counter()
    save_rgba(candidate, candidate_path, args.png_compress_level)
    timings["saveCandidateSeconds"] = round(time.perf_counter()-stage,6)

    stage = time.perf_counter()
    diff = np.any(candidate != source_rgba, axis=2)
    outside = diff & ~allowed
    fmask = fixed_mask(source_rgba.shape[:2], cfg["fixedRects"])
    fixed_changed = diff & fmask
    ys,xs = np.nonzero(diff)
    bbox = None if not xs.size else {
        "x":int(xs.min()),"y":int(ys.min()),
        "width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)
    }
    endpoint = np.asarray(cfg["landmarks"]["pedalEndpoint"], dtype=float)
    pedal = np.asarray(cfg["landmarks"]["pedalTarget"], dtype=float)
    distance = float(np.linalg.norm(endpoint-pedal))
    tolerance = float(cfg["pedalTolerancePx"])
    candidate_file_sha = sha256(candidate_path)
    qa = {
        "schemaVersion":3,
        "actionKey":cfg["actionKey"],"phase":cfg["phase"],
        "source":rel(source),"sourceSha256":source_sha,
        "brokenSource":rel(broken),"brokenSourceSha256":broken_sha,
        "fixedDrum":rel(drum),"fixedDrumSha256":drum_sha,
        "config":rel(cfg_path),"configSha256":config_sha,
        "candidate":rel(candidate_path),"candidateSha256":candidate_file_sha,
        "canvas":[int(candidate.shape[1]),int(candidate.shape[0])],"mode":"RGBA",
        "changedPixels":int(np.count_nonzero(diff)),
        "outsideAllowedChangedPixels":int(np.count_nonzero(outside)),
        "fixedRegionChangedPixels":int(np.count_nonzero(fixed_changed)),
        "changedBBox":bbox,
        "pedalEndpoint":endpoint.tolist(),"pedalTarget":pedal.tolist(),
        "pedalDistancePx":round(distance,3),"pedalTolerancePx":tolerance,
        "alphaChannelPresent":candidate.shape[2] == 4,
        "visualQaRequired":True,
        "checks":{
            "canvas1448x1086":candidate.shape[:2] == (1086,1448),
            "rgba":candidate.shape[2] == 4,
            "sourceShaMatchesConfig":expected_source in (None,"","AUTO") or source_sha == expected_source,
            "candidateDiffersFromSource":int(np.count_nonzero(diff)) > 0,
            "outsideAllowedZero":int(np.count_nonzero(outside)) == 0,
            "fixedRegionsZero":int(np.count_nonzero(fixed_changed)) == 0,
            "pedalContactWithinTolerance":distance <= tolerance,
            "runtimeWritableFalse":cfg.get("runtimeWritable") is False,
            "userApprovalPending":str(cfg.get("userApprovalStatus","")).upper() != "APPROVED",
        }
    }
    exp = cfg.get("expectedRegression",{})
    if exp:
        qa["regressionChecks"] = {
            "changedPixelsMatch": qa["changedPixels"] == exp.get("changedPixels", qa["changedPixels"]),
            "changedBBoxMatch": qa["changedBBox"] == exp.get("changedBBox", qa["changedBBox"]),
            "outsideAllowedMatch": qa["outsideAllowedChangedPixels"] == exp.get("outsideAllowedChangedPixels",0),
            "pedalDistanceMatch": abs(qa["pedalDistancePx"] - float(exp.get("pedalDistancePx",qa["pedalDistancePx"]))) <= 0.01,
        }
    else:
        qa["regressionChecks"] = {}
    qa["machinePass"] = all(qa["checks"].values()) and all(qa["regressionChecks"].values())
    timings["qaSeconds"] = round(time.perf_counter()-stage,6)

    stage = time.perf_counter()
    composite = alpha_composite_rgba(drum_rgba, candidate)
    composite_review = out_dir / GENERATED_NAMES["compositeReview"]
    save_webp(composite, composite_review)
    timings["compositeReviewSeconds"] = round(time.perf_counter()-stage,6)

    stage = time.perf_counter()
    review_path = out_dir / GENERATED_NAMES["review"]
    save_webp(candidate, review_path)
    gap = np.zeros((8, candidate.shape[1], 4), dtype=np.uint8)
    gap[:,:,3] = 255
    before_after = np.concatenate([broken_rgba, gap, candidate], axis=0)
    before_after_path = out_dir / GENERATED_NAMES["beforeAfterReview"]
    save_webp(before_after, before_after_path)
    timings["reviewImagesSeconds"] = round(time.perf_counter()-stage,6)

    timings["candidateToReviewCompleteSeconds"] = round(
        timings["warpSeconds"] + timings["saveCandidateSeconds"] + timings["qaSeconds"] +
        timings["compositeReviewSeconds"] + timings["reviewImagesSeconds"], 6)
    timings["totalSeconds"] = round(time.perf_counter()-total_start,6)

    qa_path = out_dir / GENERATED_NAMES["qa"]
    timing_path = out_dir / GENERATED_NAMES["timing"]
    manifest_path = out_dir / GENERATED_NAMES["runManifest"]
    commit_manifest_path = out_dir / GENERATED_NAMES["commitManifest"]
    regression_path = out_dir / GENERATED_NAMES["regression"]
    qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    timing_path.write_text(json.dumps({"schemaVersion":3,"stages":timings},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    generated = [candidate_path,review_path,composite_review,before_after_path,qa_path,timing_path]
    manifest = {
        "schemaVersion":2,"frame":"008","actionKey":"BD:RF","phase":"hit",
        "inputs":{
            "normalSource":{"path":rel(source),"sha256":source_sha,"cacheHit":source_hit},
            "brokenSource":{"path":rel(broken),"sha256":broken_sha,"cacheHit":broken_hit},
            "fixedDrum":{"path":rel(drum),"sha256":drum_sha,"cacheHit":drum_hit},
            "config":{"path":rel(cfg_path),"sha256":config_sha}
        },
        "outputs":[{"path":rel(p),"sha256":sha256(p)} for p in generated],
        "runtimeModified":False,"otherFramesTouched":False,
        "visualQaRequired":True,"machinePass":qa["machinePass"]
    }
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    commit_targets = generated + [manifest_path,cfg_path]
    if not qa["machinePass"]:
        commit_targets = [qa_path,timing_path,manifest_path,cfg_path]
    safe_rels = [rel(p) for p in commit_targets]
    safety = {
        "runtimePathsIncluded":[p for p in safe_rels if p.startswith(RUNTIME_PREFIX)],
        "otherFramePathsIncluded":[p for p in safe_rels if any(t in Path(p).name for t in FORBIDDEN_FRAME_TOKENS)]
    }
    commit_manifest = {
        "schemaVersion":2,"machinePass":qa["machinePass"],
        "eligibleForCandidateCommit":qa["machinePass"] and not safety["runtimePathsIncluded"] and not safety["otherFramePathsIncluded"],
        "paths":safe_rels,"safety":safety
    }
    commit_manifest_path.write_text(json.dumps(commit_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    regression = {
        "schemaVersion":1,"frame":"008","machinePass":qa["machinePass"],
        "visualQaRequired":True,"userApprovalStatus":cfg.get("userApprovalStatus"),
        "runtimeModified":False,"otherFramesTouched":False,
        "outsideAllowedChangedPixels":qa["outsideAllowedChangedPixels"],
        "fixedRegionChangedPixels":qa["fixedRegionChangedPixels"],
        "candidateCanvas":qa["canvas"],"candidateMode":qa["mode"],
        "timings":timings,"candidateSha256":candidate_file_sha,
        "sourceSha256":source_sha,"fixedDrumSha256":drum_sha,"configSha256":config_sha
    }
    regression_path.write_text(json.dumps(regression,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    if args.git_commit:
        if not qa["machinePass"]:
            raise RuntimeError("machine QA failed; candidate commit blocked")
        if not args.start_main_sha:
            raise RuntimeError("--start-main-sha required with --git-commit")
        guarded = generated + [manifest_path,commit_manifest_path,regression_path,cfg_path]
        commit_sha = guarded_commit(guarded,args.start_main_sha,args.commit_message)
        print(json.dumps({"machinePass":True,"commitSha":commit_sha,"timings":timings},ensure_ascii=False))
    else:
        print(json.dumps({"machinePass":qa["machinePass"],"timings":timings,"commitEligible":commit_manifest["eligibleForCandidateCommit"]},ensure_ascii=False))
    return 0 if qa["machinePass"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
