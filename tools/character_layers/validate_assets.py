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
    if actual!=listed: errors.append(f"layer PNG set mismatch actual={sorted(actual)} listed={sorted(listed)}")
    if len(listed)!=2: errors.append("baseline reset requires exactly 2 layer PNGs")
    drum="character-assets/layers/drum/drum_base.png"
    de=next((a for a in assets_manifest["assets"] if a["path"]==drum),None)
    if not de or de["sha256"]!=assets_manifest.get("lockedDrumSha256"): errors.append("locked drum SHA mismatch")
    required=inventory.get("requiredFrames",{})
    if inventory.get("imageSetState")=="baseline-only" and set(required)!={"neutral"}: errors.append("baseline-only must expose only neutral frame")
    for fid,frame in required.items():
        rel="character-assets/"+frame["path"]
        if rel not in listed: errors.append(f"{fid}: missing registered frame")
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
    if len(scoped)!=scope["noteCount"] or len(groups)!=scope["groupCount"]: errors.append("runtime scope count mismatch")
    if {key(g) for g in groups}!=set(scope["expectedKeys"]): errors.append("runtime key set mismatch")
    for g in groups:
        k=key(g)
        if inventory["runtimeFrameMap"].get(k)!="neutral": errors.append(f"{k}: baseline frame must be neutral")
        phases=inventory["runtimePhaseFrameMap"].get(k,{})
        if phases!={"prep":"neutral","hit":"neutral","rebound":"neutral"}: errors.append(f"{k}: baseline phases must be neutral")
    if errors:
        print("Character asset validation failed:")
        for e in errors: print("- "+e)
        return 1
    print(f"Character asset validation OK. Canvas={size[0]}x{size[1]}, registered PNGs=2, runtime measures=1-4, notes={len(scoped)}, groups={len(groups)}")
    return 0
if __name__=="__main__": sys.exit(main())
