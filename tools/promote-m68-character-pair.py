from __future__ import annotations
import hashlib, json, shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STAGING=ROOT/"character-assets/promotion-staging/m68_bd_rc_sn_attempt01.json"
INV=ROOT/"character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json"
MAN=ROOT/"character-assets/config/assets_manifest.json"
MAP=ROOT/"character-assets/prototypes/luna_say_maybe_16m/ACTION_KEY_ASSET_MAP.json"

EXPECTED={
 "hit":"0ca0d673e70fd0072ceac0fb6ac8d5b7088a828263e9239d38edb9312cdb163e",
 "rebound":"5584de18ef1d912b377208e805593de37a26cf6946efc41356297cb20836d619",
}
CAND={
 "hit":ROOT/"character-assets/review-candidates/m68/bd_rc_sn_rf_r_l_hit_attempt01.png",
 "rebound":ROOT/"character-assets/review-candidates/m68/bd_rc_sn_rf_r_l_rebound_attempt01.png",
}
FORMAL={
 "hit":ROOT/"character-assets/layers/character/combo/bd_rc_sn_rf_r_l_hit_refresh.png",
 "rebound":ROOT/"character-assets/layers/character/combo/bd_rc_sn_rf_r_l_rebound_refresh.png",
}
ASSETKEY={
 "hit":"bd_rc_sn_rf_r_l_hit_refresh",
 "rebound":"bd_rc_sn_rf_r_l_rebound_refresh",
}
ACTION="BD+RC+SN:RF/R/L"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

for phase in ("hit","rebound"):
    actual=sha(CAND[phase])
    if actual!=EXPECTED[phase]:
        raise SystemExit(f"{phase} candidate SHA mismatch: {actual}")
    FORMAL[phase].parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(CAND[phase],FORMAL[phase])
    if sha(FORMAL[phase])!=EXPECTED[phase]:
        raise SystemExit(f"{phase} formal copy SHA mismatch")

st=load(STAGING)
if st.get("status") not in ("APPROVED_FOR_PROMOTION","PROMOTED"):
    raise SystemExit(f"unexpected staging status {st.get('status')}")
st["status"]="PROMOTED"
save(STAGING,st)

inv=load(INV)
rf=inv.setdefault("requiredFrames",{})
for phase in ("hit","rebound"):
    rf[ASSETKEY[phase]]={
      "path":f"layers/character/combo/bd_rc_sn_rf_r_l_{phase}_refresh.png",
      "state":"ready",
      "sha256":EXPECTED[phase],
      "actionKey":ACTION,
      "phase":phase
    }
inv.setdefault("runtimeFrameMap",{})[ACTION]=ASSETKEY["hit"]
inv.setdefault("runtimePhaseFrameMap",{})[ACTION]={
  "prep":"neutral","hit":ASSETKEY["hit"],"rebound":ASSETKEY["rebound"]
}
inv["missingExactFrames"]=[x for x in inv.get("missingExactFrames",[]) if ACTION not in str(x)]
inv["updatedAt"]="2026-09-19T13:36:00+09:00"
save(INV,inv)

man=load(MAN)
entries=man.setdefault("assets",[])
for phase in ("hit","rebound"):
    rel=f"character-assets/layers/character/combo/bd_rc_sn_rf_r_l_{phase}_refresh.png"
    item=next((x for x in entries if x.get("path")==rel),None)
    if item is None:
        item={}
        entries.append(item)
    item.update({
      "path":rel,"width":1448,"height":1086,"x":0,"y":0,
      "sha256":EXPECTED[phase],
      "status":"FORMAL_QA_PASSED_RUNTIME_PENDING",
      "purpose":f"Luna M68 BD+RC+SN:RF/R/L formal {phase}; exact RC+SN formal parent plus approved local BD cue.",
      "part":"BD+RC+SN","phase":phase,"hand":"RF/R/L",
      "notes":[
        "Deterministic cue composition; fixed-drum visual QA PASS.",
        f"Dropbox exact bytes saved /ChatGPT/dtx-drum-flow/bd_rc_sn_rf_r_l_{phase}_attempt01.png",
        "Build run 35421113802 artifact 10577777737."
      ]
    })
man["authoritativeImageCount"]=len(entries)
man["updatedAt"]="2026-09-19T13:36:00+09:00"
save(MAN,man)

am=load(MAP)
entry=next((x for x in am.get("entries",[]) if x.get("actionKey")==ACTION),None)
if entry is None:
    raise SystemExit("M68 action entry missing from ACTION_KEY_ASSET_MAP")
entry.update({
 "prepAsset":"character-assets/layers/character/base/neutral.png",
 "hitAsset":"character-assets/layers/character/combo/bd_rc_sn_rf_r_l_hit_refresh.png",
 "reboundAsset":"character-assets/layers/character/combo/bd_rc_sn_rf_r_l_rebound_refresh.png",
 "classification":"FORMAL_QA_PASSED_RUNTIME_PENDING",
 "manifestStatus":"FORMAL_QA_PASSED_RUNTIME_PENDING",
 "runtimeMapped":True,
 "qaStatus":"PRE_RUNTIME_QA_PASSED",
 "missing":False,
 "blocked":False,
 "hitSha256":EXPECTED["hit"],
 "reboundSha256":EXPECTED["rebound"],
 "method":"formal RC+SN:R/L exact bytes plus proven deterministic local BD cue"
})
am["updatedAt"]="2026-09-19T13:36:00+09:00"
save(MAP,am)
print("M68 formal promotion prepared successfully")
