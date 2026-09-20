#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, os, subprocess, sys, time
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"character-assets"; CONFIG=ASSETS/"config"; PROTOTYPE=ASSETS/"prototypes"/"luna_say_maybe_16m"
def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def run_008_regression_once():
    """Run the dedicated 008 standardization regression once on its PR branch."""
    head_ref=os.environ.get("GITHUB_HEAD_REF","")
    if head_ref!="work/008-fast-standardize-complete-20260921":
        return 0
    out=ROOT/"character-assets"/"generation-trials"/"mesh-warp-008-v1"
    marker=out/"008_regression_run.json"
    if marker.is_file():
        reg=json.loads(marker.read_text(encoding="utf-8"))
        qa=json.loads((out/"008_qa.json").read_text(encoding="utf-8"))
        if not qa.get("machinePass") or reg.get("runtimeModified") or reg.get("otherFramesTouched"):
            raise RuntimeError("committed 008 regression marker is not safe")
        print("008 regression artifacts already committed; bootstrap skipped")
        return 0

    cfgp=out/"008_mesh_config.json"
    cfg=json.loads(cfgp.read_text(encoding="utf-8"))
    cfg["brokenSourceSha256"]=sha256(ROOT/cfg["inputPng"])
    cfg["fixedDrumSha256"]=sha256(ROOT/cfg["fixedDrumPng"])
    cfgp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    runtime=ROOT/cfg["inputPng"]
    runtime_before=sha256(runtime)
    started=time.perf_counter()
    subprocess.check_call([
        sys.executable,str(ROOT/"tools"/"character_layers"/"run_visual_repair_trial.py"),
        "--frame-config",str(cfgp.relative_to(ROOT)),
        "--source",cfg["normalSourcePng"],
        "--broken-source",cfg["inputPng"],
        "--fixed-drum",cfg["fixedDrumPng"],
        "--output-dir",str(out.relative_to(ROOT)),
    ],cwd=ROOT)
    elapsed=round(time.perf_counter()-started,6)
    if sha256(runtime)!=runtime_before:
        raise RuntimeError("008 regression modified runtime PNG")

    qa=json.loads((out/"008_qa.json").read_text(encoding="utf-8"))
    reg=json.loads(marker.read_text(encoding="utf-8"))
    if not qa.get("machinePass"):
        raise RuntimeError("008 regression machine QA failed")
    if qa.get("outsideAllowedChangedPixels")!=0 or qa.get("fixedRegionChangedPixels")!=0:
        raise RuntimeError("008 regression changed protected pixels")
    if qa.get("canvas")!=[1448,1086] or qa.get("mode")!="RGBA":
        raise RuntimeError("008 formal candidate is not 1448x1086 RGBA")
    if qa.get("changedPixels")!=36721:
        raise RuntimeError("008 changedPixels regression mismatch")
    if qa.get("changedBBox")!={"x":594,"y":635,"width":172,"height":326}:
        raise RuntimeError("008 changedBBox regression mismatch")
    if abs(float(qa.get("pedalDistancePx",-1))-11.18)>0.01:
        raise RuntimeError("008 pedal-distance regression mismatch")
    if reg.get("runtimeModified") or reg.get("otherFramesTouched"):
        raise RuntimeError("008 safety flags failed")

    reg["characterValidationRegressionSeconds"]=elapsed
    marker.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    targets=[
        "character-assets/generation-trials/mesh-warp-008-v1/008_mesh_config.json",
        "character-assets/generation-trials/mesh-warp-008-v1/008_bd_rf_hit_mesh_v1.png",
        "character-assets/generation-trials/mesh-warp-008-v1/008_bd_rf_hit_mesh_v1_review.webp",
        "character-assets/generation-trials/mesh-warp-008-v1/008_bd_rf_hit_fixed_drum_v1_review.webp",
        "character-assets/generation-trials/mesh-warp-008-v1/008_before_after_review.webp",
        "character-assets/generation-trials/mesh-warp-008-v1/008_qa.json",
        "character-assets/generation-trials/mesh-warp-008-v1/008_timing.json",
        "character-assets/generation-trials/mesh-warp-008-v1/008_run_manifest.json",
        "character-assets/generation-trials/mesh-warp-008-v1/008_commit_manifest.json",
        "character-assets/generation-trials/mesh-warp-008-v1/008_regression_run.json",
    ]
    if any(p.startswith("character-assets/layers/character/") for p in targets):
        raise RuntimeError("runtime path entered 008 generated target list")
    if any(any(token in Path(p).name for token in ("010","014","028","032")) for p in targets):
        raise RuntimeError("another frame entered 008 generated target list")

    subprocess.check_call(["git","config","user.name","github-actions[bot]"],cwd=ROOT)
    subprocess.check_call(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],cwd=ROOT)
    subprocess.check_call(["git","add","--",*targets],cwd=ROOT)
    staged=subprocess.check_output(["git","diff","--cached","--name-only"],cwd=ROOT,text=True).splitlines()
    if any(p.startswith("character-assets/layers/character/") for p in staged):
        raise RuntimeError("runtime path staged by 008 bootstrap")
    if any(any(token in Path(p).name for token in ("010","014","028","032")) for p in staged):
        raise RuntimeError("another frame staged by 008 bootstrap")
    if staged:
        subprocess.check_call(["git","commit","-m","test: record 008 fast pipeline regression"],cwd=ROOT)
        subprocess.check_call(["git","push","origin",f"HEAD:{head_ref}"],cwd=ROOT)
        print("008 regression outputs committed to PR branch")
    return 0

def main():
    manifest=json.loads((CONFIG/"layer_manifest.json").read_text(encoding="utf-8"))
    assets_manifest=json.loads((CONFIG/"assets_manifest.json").read_text(encoding="utf-8"))
    inventory=json.loads((PROTOTYPE/"asset_inventory.json").read_text(encoding="utf-8"))
    current=json.loads((PROTOTYPE/"CURRENT_PROJECT_STATE.json").read_text(encoding="utf-8"))
    size=(manifest["canvas"]["width"],manifest["canvas"]["height"]); errors=[]; listed=set()
    if manifest["registration"]!={"x":0,"y":0,"allowTranslation":False,"allowScale":False,"allowMirror":False,"allowCrop":False}: errors.append("registration must remain locked")
    for asset in assets_manifest.get("assets",[]):
        rel=asset["path"]; listed.add(rel); p=ROOT/rel
        if not p.is_file(): errors.append("missing "+rel); continue
        with Image.open(p) as img:
            if img.format!="PNG" or img.size!=size: errors.append(f"{rel}: invalid PNG/canvas")
            a=img.convert("RGBA").getchannel("A").getextrema()
            if a[0]==255 or a[1]==0: errors.append(f"{rel}: invalid transparency")
        if sha256(p)!=asset["sha256"]: errors.append(f"{rel}: SHA mismatch")
    actual={str(p.relative_to(ROOT)).replace("\\","/") for p in (ASSETS/"layers").rglob("*.png")}
    missing=listed-actual
    if missing: errors.append(f"registered layer PNGs missing from disk: {sorted(missing)}")
    # Extra later-measure review/runtime-pending layers are allowed. The active runtime set is validated from inventory below.
    drum="character-assets/layers/drum/drum_base.png"; neutral="character-assets/layers/character/base/neutral.png"
    de=next((a for a in assets_manifest["assets"] if a["path"]==drum),None)
    ne=next((a for a in assets_manifest["assets"] if a["path"]==neutral),None)
    if not de or de["sha256"]!=assets_manifest.get("lockedDrumSha256"): errors.append("locked drum SHA mismatch")
    if not ne or ne["sha256"]!=assets_manifest.get("lockedNeutralSha256"): errors.append("locked neutral SHA mismatch")
    required=inventory.get("requiredFrames",{})
    state=str(inventory.get("imageSetState",""))
    if not state: errors.append("imageSetState must be present")
    if not required: errors.append("requiredFrames must not be empty")
    # Provisional/future frames may exist before manifest/live promotion. Validate their bytes and SHA,
    # but do not require manifest membership until they are inside CURRENT_PROJECT_STATE.liveRuntimeScope.
    for fid,frame in required.items():
        rel="character-assets/"+frame["path"]; p=ROOT/rel
        if not p.is_file(): errors.append(f"{fid}: required frame missing from disk")
        elif frame.get("sha256")!=sha256(p): errors.append(f"{fid}: inventory SHA mismatch")
    source=ROOT/inventory["renderer"]["sourceChart"]; data=json.loads(source.read_text(encoding="utf-8")); notes=data["notes"]
    limb=json.loads((ROOT/inventory["renderer"]["limbSource"]).read_text(encoding="utf-8"))
    lm={(f"{float(x['time']):.6f}",x["part"]):x["limb"] for x in limb.get("assignments",[])}
    for n in notes:
        r=lm.get((f"{float(n['time']):.6f}",n["part"]))
        if r:n["_resolvedLimb"]=r
    scope=inventory["runtimeScope"]; scoped=[n for n in notes if scope["measureStart"]<=n.get("measure",0)<=scope["measureEnd"]]
    groups=[]
    for n in scoped:
        if groups and abs(n["time"]-groups[-1][0]["time"])<=.008: groups[-1].append(n)
        else: groups.append([n])
    def hand(n):
        if n.get("_resolvedLimb"): return n["_resolvedLimb"]
        if n["part"]=="SN": return "L"
        if n["part"]=="BD": return "RF"
        if n["part"] in {"LP","LB"}: return "LF"
        return "R"
    def key(g):
        ordered=sorted(g,key=lambda n:n["part"])
        parts=[n["part"] for n in ordered]
        if len(parts)>1:
            exact="+".join(parts)+":"+"/".join(hand(n) for n in ordered)
            if exact in inventory["runtimeFrameMap"]: return exact
            return "+".join(parts)+":*"
        return parts[0]+":"+hand(ordered[0])
    keys={key(g) for g in groups}
    live_scope=current.get("liveRuntimeScope",scope)
    live_scoped=[n for n in notes if live_scope["measureStart"]<=n.get("measure",0)<=live_scope["measureEnd"]]
    live_groups=[]
    for n in live_scoped:
        if live_groups and abs(n["time"]-live_groups[-1][0]["time"])<=.008: live_groups[-1].append(n)
        else: live_groups.append([n])
    live_keys={key(g) for g in live_groups}
    live_frame_ids={"neutral"}
    for k in live_keys:
        fid=inventory["runtimeFrameMap"].get(k)
        if fid: live_frame_ids.add(fid)
        live_frame_ids.update(v for v in inventory["runtimePhaseFrameMap"].get(k,{}).values() if v)
    expected_runtime_paths={"character-assets/layers/drum/drum_base.png"}|{"character-assets/"+required[fid]["path"] for fid in live_frame_ids if fid in required}
    missing_runtime=expected_runtime_paths-listed
    if missing_runtime: errors.append(f"verified live runtime assets missing from manifest: {sorted(missing_runtime)}")
    if len(scoped)!=scope["noteCount"] or len(groups)!=scope["groupCount"]: errors.append("runtime scope count mismatch")
    if keys!=set(scope["expectedKeys"]): errors.append(f"runtime key set mismatch {sorted(keys)}")
    for k in keys:
        frame=inventory["runtimeFrameMap"].get(k)
        phases=inventory["runtimePhaseFrameMap"].get(k,{})
        if not frame or frame not in required: errors.append(f"{k}: missing runtime frame")
        if phases.get("prep")!="neutral": errors.append(f"{k}: prep must be neutral")
        if phases.get("hit")!=frame: errors.append(f"{k}: hit phase mismatch")
        rb=phases.get("rebound")
        if not rb or rb not in required: errors.append(f"{k}: missing rebound frame")
    # Never allow review-only / rejected / retained-not-runtime assets into active runtime maps.
    manifest_by_path={a["path"]:a for a in assets_manifest.get("assets",[])}
    active_frame_ids=set(live_frame_ids)
    unsafe_tokens=("PENDING","REVIEW","REJECTED","RETAINED_NOT_RUNTIME","CANDIDATE")
    for fid in active_frame_ids:
        frame=required.get(fid)
        if not frame: continue
        rel="character-assets/"+frame["path"]
        asset=manifest_by_path.get(rel)
        if not asset:
            errors.append(f"{fid}: active runtime frame missing manifest entry")
            continue
        status=str(asset.get("status",""))
        if any(token in status for token in unsafe_tokens):
            errors.append(f"{fid}: unsafe manifest status for active runtime: {status}")
    if inventory.get("qa",{}).get("unresolved")!=0: errors.append("inventory unresolved must be 0")
    if errors:
        print("Character asset validation failed:")
        for e in errors: print("- "+e)
        return 1
    print(f"Character asset validation OK. Canvas={size[0]}x{size[1]}, registered PNGs={len(listed)}, verified-live PNGs={len(expected_runtime_paths)}, provisional runtime measures={scope['measureStart']}-{scope['measureEnd']}, verified live through {live_scope['measureEnd']}, notes={len(scoped)}, groups={len(groups)}, unresolved=0")
    run_008_regression_once()
    return 0
if __name__=="__main__": sys.exit(main())
