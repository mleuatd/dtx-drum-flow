#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, sys
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"character-assets"; CONFIG=ASSETS/"config"; PROTOTYPE=ASSETS/"prototypes"/"luna_say_maybe_16m"
def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def main():
    manifest=json.loads((CONFIG/"layer_manifest.json").read_text(encoding="utf-8"))
    assets_manifest=json.loads((CONFIG/"assets_manifest.json").read_text(encoding="utf-8"))
    inventory=json.loads((PROTOTYPE/"asset_inventory.json").read_text(encoding="utf-8"))
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
    expected_runtime_paths={"character-assets/layers/drum/drum_base.png"}|{"character-assets/"+frame["path"] for frame in required.values()}
    if len(expected_runtime_paths)!=12: errors.append(f"active M1-4 runtime set must resolve to 12 layer PNGs, got {len(expected_runtime_paths)}")
    missing_runtime=expected_runtime_paths-listed
    if missing_runtime: errors.append(f"active runtime assets missing from manifest: {sorted(missing_runtime)}")
    if inventory.get("imageSetState")!="m1-4-complete": errors.append("imageSetState must be m1-4-complete")
    if len(required)!=11: errors.append(f"requiredFrames must contain 11 character frames, got {len(required)}")
    for fid,frame in required.items():
        rel="character-assets/"+frame["path"]
        if rel not in listed: errors.append(f"{fid}: missing registered frame")
        elif frame.get("sha256")!=sha256(ROOT/rel): errors.append(f"{fid}: inventory SHA mismatch")
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
        if n["part"] in {"BD","LB"}: return "RF"
        if n["part"]=="LP": return "LF"
        return "R"
    def key(g):
        parts=sorted({n["part"] for n in g})
        if len(parts)>1:return "+".join(parts)+":*"
        return parts[0]+":"+hand(g[0])
    keys={key(g) for g in groups}
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
    if inventory.get("qa",{}).get("unresolved")!=0: errors.append("inventory unresolved must be 0")
    if errors:
        print("Character asset validation failed:")
        for e in errors: print("- "+e)
        return 1
    print(f"Character asset validation OK. Canvas={size[0]}x{size[1]}, registered PNGs={len(listed)}, active runtime PNGs={len(expected_runtime_paths)}, runtime measures={scope['measureStart']}-{scope['measureEnd']}, notes={len(scoped)}, groups={len(groups)}, unresolved=0")
    return 0
if __name__=="__main__": sys.exit(main())
