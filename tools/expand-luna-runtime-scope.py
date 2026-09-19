from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=int(sys.argv[1]) if len(sys.argv)>1 else 40
invp=ROOT/"character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json"
notesp=ROOT/"site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json"
limbsp=ROOT/"site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json"
inv=json.loads(invp.read_text()); chart=json.loads(notesp.read_text()); limbs=json.loads(limbsp.read_text())
lm={(f'{float(x["time"]):.6f}',x["part"]):x["limb"] for x in limbs.get("assignments",[])}
notes=[]
for n in chart.get("notes",[]):
    if int(n.get("measure",0))>TARGET: continue
    x=dict(n); x["limb"]=lm.get((f'{float(n["time"]):.6f}',n["part"]),x.get("limb"))
    if not x.get("limb"): raise SystemExit(f'missing limb {x}')
    notes.append(x)
groups=[]
for n in notes:
    if groups and abs(float(n["time"])-float(groups[-1][0]["time"]))<=.008: groups[-1].append(n)
    else: groups.append([n])
def exact(g):
    a=sorted(g,key=lambda x:x["part"])
    if len(a)>1:return "+".join(x["part"] for x in a)+":"+"/".join(x["limb"] for x in a)
    return a[0]["part"]+":"+a[0]["limb"]
def key(g):
    e=exact(g)
    if e in inv["runtimeFrameMap"]: return e
    parts=sorted(set(x["part"] for x in g))
    w="+".join(parts)+":*"
    return w if len(parts)>1 and w in inv["runtimeFrameMap"] else e
keys=[]; unresolved=[]
for g in groups:
    k=key(g)
    if k not in inv["runtimeFrameMap"]: unresolved.append(k); continue
    phases=inv.setdefault("runtimePhaseFrameMap",{}).setdefault(k,{})
    phases.setdefault("prep","neutral")
    for ph in ("prep","hit","rebound"):
        fid=phases.get(ph)
        if not fid or fid not in inv.get("requiredFrames",{}): unresolved.append(f"{k}.{ph}")
    if k not in keys: keys.append(k)
if unresolved: raise SystemExit("unresolved: "+", ".join(sorted(set(unresolved))))
inv["runtimeScope"]={"measureStart":1,"measureEnd":TARGET,"noteCount":len(notes),"groupCount":len(groups),"firstNoteTime":min(float(n["time"]) for n in notes),"lastNoteTime":max(float(n["time"]) for n in notes),"expectedKeys":keys}
inv["scope"]=f"Luna Say Maybe measures 1-{TARGET} runtime mapped; public runtime QA pending"
inv["imageSetState"]=f"m1-{TARGET}-runtime-qa-pending"
inv["updatedAt"]="2026-09-19T10:39:00+09:00"
inv["note"]=f"Runtime scope expanded deterministically from FINAL chart + full limb assignments through M{TARGET}; all exact/wildcard keys and prep/hit/rebound frames resolved before write."
invp.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(inv["runtimeScope"],ensure_ascii=False,indent=2))
