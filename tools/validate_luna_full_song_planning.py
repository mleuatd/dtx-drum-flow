from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
chart=load("site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json")
limbs=load("site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json")
action_inv=load("character-assets/prototypes/luna_say_maybe_16m/FULL_SONG_ACTION_KEY_INVENTORY.json")
asset_plan=load("character-assets/prototypes/luna_say_maybe_16m/FULL_SONG_ASSET_IMPLEMENTATION_PLAN.json")
block_plan=load("character-assets/prototypes/luna_say_maybe_16m/FULL_SONG_IMPLEMENTATION_BLOCK_PLAN.json")
runtime=load("character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json")
manifest=load("character-assets/config/assets_manifest.json")
lm={(round(float(x["time"]),6),x["part"]):x["limb"] for x in limbs["assignments"]}
groups=[]
for n in chart["notes"]:
    x=dict(n); x["limb"]=lm[(round(float(n["time"]),6),n["part"])]
    if groups and abs(float(x["time"])-float(groups[-1][0]["time"]))<=.008: groups[-1].append(x)
    else: groups.append([x])
def action_key(g):
    a=sorted(g,key=lambda x:x["part"])
    if len(a)==1:return f'{a[0]["part"]}:{a[0]["limb"]}'
    return "+".join(x["part"] for x in a)+":"+"/".join(x["limb"] for x in a)
counts={}
meta={}
for g in groups:
    k=action_key(g); counts[k]=counts.get(k,0)+1
    m=meta.setdefault(k,{"firstMeasure":g[0]["measure"],"lastMeasure":g[0]["measure"],"firstTime":g[0]["time"],"lastTime":g[0]["time"]})
    m["lastMeasure"]=g[0]["measure"];m["lastTime"]=g[0]["time"]
assert counts==action_inv["actionKeyCounts"],"full-song action inventory drift"
planned={a["actionKey"]:a for a in asset_plan["actions"]}
assert set(planned)==set(counts),f"asset plan key coverage mismatch: missing={sorted(set(counts)-set(planned))}, extra={sorted(set(planned)-set(counts))}"
allowed={"REUSE_APPROVED","REUSE_NEEDS_RUNTIME_QA","NEW_IMAGE_REQUIRED","BLOCKED","REJECTED_NEVER_USE"}
assert all(a["classification"] in allowed for a in planned.values()),"invalid asset classification"
for k,a in planned.items():
    assert a["count"]==counts[k],f"{k}: occurrence count mismatch"
    assert a["firstMeasure"]==meta[k]["firstMeasure"] and a["lastMeasure"]==meta[k]["lastMeasure"],f"{k}: measure range mismatch"
manifest_paths={x["path"] for x in manifest["assets"]}
def runtime_key(k):
    parts=k.split(":",1)[0]
    return parts+":*" if "+" in parts else k
for k,a in planned.items():
    rk=runtime_key(k)
    if a["classification"]=="REUSE_APPROVED":
        assert a["existingHit"] and a["existingRebound"],f"{k}: approved reuse missing asset path"
        assert a["existingHit"] in manifest_paths and a["existingRebound"] in manifest_paths,f"{k}: approved reuse missing manifest asset"
        assert rk in runtime["runtimeFrameMap"],f"{k}: approved reuse missing runtime mapping"
    elif a["classification"]=="REUSE_NEEDS_RUNTIME_QA":
        assert a["existingHit"] in manifest_paths and a["existingRebound"] in manifest_paths,f"{k}: runtime-QA reuse missing manifest asset"
        assert rk not in runtime["runtimeFrameMap"],f"{k}: pending asset unexpectedly runtime-mapped"
    elif a["classification"]=="NEW_IMAGE_REQUIRED":
        assert not a["existingHit"] and not a["existingRebound"],f"{k}: new-image key unexpectedly has existing asset"
    elif a["classification"]=="BLOCKED":
        assert not a["existingHit"] and not a["existingRebound"],f"{k}: blocked key unexpectedly has approved asset"
missing=asset_plan["missingAssets"]
for k,a in planned.items():
    if a["classification"] in {"NEW_IMAGE_REQUIRED","BLOCKED"}:
        phases=[x["phase"] for x in missing if x["actionKey"]==k]
        assert sorted(phases)==["hit","rebound"],f"{k}: missing hit/rebound requirement"
scope=runtime["runtimeScope"]
assert (scope["measureStart"],scope["measureEnd"])==(1,8),"planning must not expand live runtimeScope"
blocks=block_plan["blocks"]
assert blocks[0]["measureStart"]==9 and blocks[-1]["measureEnd"]==148,"block coverage endpoints wrong"
for a,b in zip(blocks,blocks[1:]): assert a["measureEnd"]+1==b["measureStart"],f"block gap/overlap {a['blockId']}->{b['blockId']}"
print(f"PASS Luna planning validation: {len(counts)} action keys, {len(groups)} groups, live scope 1-8, {len(blocks)} blocks")
