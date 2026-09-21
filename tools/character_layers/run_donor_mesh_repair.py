#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "character-assets/config/donor_mesh"
GLOBAL = SPEC / "global_rules.json"
PARENT = SPEC / "parent_manifest.json"

def loadj(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def git_show_bytes(commit: str, repo_path: str) -> bytes:
    return subprocess.check_output(["git","show",f"{commit}:{repo_path}"], cwd=ROOT)

def resolve_locked_parent(logical: str, manifest: dict) -> bytes:
    overlays = manifest.get("overlays", {})
    if logical in overlays:
        ov = overlays[logical]
        repo_source = ov.get("repoSourcePath")
        if not repo_source:
            raise RuntimeError(f"overlay requires explicit repoSourcePath before use: {logical}")
        b = (ROOT / repo_source).read_bytes()
        if sha256_bytes(b) != ov["sha256"]:
            raise RuntimeError(f"overlay SHA mismatch: {logical}")
        return b
    repo_path = f"{manifest['baselineRelativeRoot'].rstrip('/')}/{logical}"
    return git_show_bytes(manifest["basisCommit"], repo_path)

def rgba_from_bytes(b: bytes) -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        f.write(b); f.flush()
        return np.array(Image.open(f.name).convert("RGBA"))

def alpha_bbox(a: np.ndarray):
    ys,xs=np.nonzero(a[:,:,3] > 0)
    if not xs.size: return None
    return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]

def alpha_area(a: np.ndarray) -> int:
    return int(np.count_nonzero(a[:,:,3] > 0))

def direct_replacement_gate(base: np.ndarray, repl: np.ndarray, rules: dict):
    gb=rules["directReplacementGate"]
    bb,rb=alpha_bbox(base),alpha_bbox(repl)
    if bb is None or rb is None: return False, {"reason":"empty alpha bbox"}
    edge=max(abs(x-y) for x,y in zip(bb,rb))
    ratio=alpha_area(repl)/max(1,alpha_area(base))
    ok=edge <= gb["alphaBBoxEdgeDeltaMaxPx"] and gb["alphaAreaRatioMin"] <= ratio <= gb["alphaAreaRatioMax"]
    return ok, {"baseBBox":bb,"replacementBBox":rb,"maxEdgeDeltaPx":edge,"alphaAreaRatio":ratio}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--frame-config", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args=ap.parse_args()
    rules=loadj(GLOBAL); parent=loadj(PARENT); cfg=loadj(ROOT/args.frame_config)
    if rules["parentAuthority"]["latestMainMayBecomeAutomaticParent"]:
        raise RuntimeError("global safety misconfigured")
    logical=cfg["frame"]
    base_b=resolve_locked_parent(logical,parent)
    base=rgba_from_bytes(base_b)
    if base.shape != (1086,1448,4):
        raise RuntimeError("locked parent canvas/mode mismatch")
    cat=cfg["repairCategory"]
    out=args.output if args.output.is_absolute() else ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    report={"schemaVersion":1,"issueId":cfg["issueId"],"frame":logical,"repairCategory":cat}
    if cat=="LOCAL_ARTIFACT_REMOVAL":
        r=cfg["allowedRoi"]; x1,y1,x2,y2=[int(r[k]) for k in ("x1","y1","x2","y2")]
        cand=base.copy(); cand[y1:y2,x1:x2]=0
        diff=np.any(cand!=base,axis=2)
        outside=diff.copy(); outside[y1:y2,x1:x2]=False
        report.update({"changedPixels":int(diff.sum()),"outsideAllowedChangedPixels":int(outside.sum()),"machinePass":int(outside.sum())==0})
    elif cat=="DIRECT_SAME_ACTION_REPLACEMENT":
        repl=rgba_from_bytes(resolve_locked_parent(cfg["replacementLogicalPath"],parent))
        ok,metrics=direct_replacement_gate(base,repl,rules)
        report["directReplacementRegistration"]=metrics
        report["machinePass"]=ok
        if not ok: raise RuntimeError("DIRECT replacement blocked by registration gate")
        cand=repl
    else:
        raise RuntimeError("Use run_visual_repair_trial.py for mesh categories after resolved control points are present.")
    Image.fromarray(cand,"RGBA").save(out,compress_level=1)
    report["candidateSha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
    report["visualQaRequired"]=True
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
