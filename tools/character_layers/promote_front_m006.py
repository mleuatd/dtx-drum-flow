#!/usr/bin/env python3
import hashlib, json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m006"
EXPECTED={
 "hit":"7da76d13cbedff3390cb6b95babac5fd8e42ebe2ef3abbe9cfcdf39a3d586ab4",
 "rebound":"38bd82c3f3df41cdb04433db55749107ae542bfcaee3c2c4a3fa83db3d363110",
}
FORMAL={
 "hit":ROOT/"character-assets/layers/character/combo/bd_rd_rf_r_hit_refresh.png",
 "rebound":ROOT/"character-assets/layers/character/combo/bd_rd_rf_r_rebound_refresh.png",
}
BP=ROOT/"character-assets/prototypes/luna_say_maybe_16m/MOTION_DEFECT_BACKLOG.json"
IP=ROOT/"character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json"
AP=ROOT/"character-assets/prototypes/luna_say_maybe_16m/ACTION_KEY_ASSET_MAP.json"
MP=ROOT/"character-assets/config/assets_manifest.json"
STATE=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m006/M006_RUNTIME_QA_STATE.json"

summary=json.loads((WORK/"M006_SUMMARY.json").read_text())
assert summary.get("pairMachinePass") is True,summary
by={x["phase"]:x for x in summary["phases"]}
for ph in ("hit","rebound"):
    assert by[ph]["candidateSha256"]==EXPECTED[ph],(ph,by[ph]["candidateSha256"])
    shutil.copyfile(ROOT/by[ph]["candidate"],FORMAL[ph])
    got=hashlib.sha256(FORMAL[ph].read_bytes()).hexdigest()
    assert got==EXPECTED[ph],(ph,got)

backlog=json.loads(BP.read_text()); inv=json.loads(IP.read_text()); amap=json.loads(AP.read_text()); manifest=json.loads(MP.read_text())
x=next(v for v in backlog["defects"] if v["issueId"]=="MOTION-006")
claim=x.get("claim") or {}
assert claim.get("owner")=="CHATGPT-FRONT" and claim.get("batch")=="FRONT-M006-AFTER-M010",claim
vq=x.get("visualIntegrityQa") or {}; ev=vq.get("reviewEvidence") or {}
assert vq.get("humanAnatomy")=="PASS" and vq.get("linework")=="PASS" and vq.get("fixedDrumComposite")=="PASS" and not vq.get("promotionBlocked")
assert ev.get("candidateHitSha256")==EXPECTED["hit"] and ev.get("candidateReboundSha256")==EXPECTED["rebound"]

paths={
 "hit":"character-assets/layers/character/combo/bd_rd_rf_r_hit_refresh.png",
 "rebound":"character-assets/layers/character/combo/bd_rd_rf_r_rebound_refresh.png",
}
for ph in ("hit","rebound"):
    full=paths[ph]; rel=full.replace("character-assets/","",1); sha=EXPECTED[ph]
    found=False
    for a in manifest.get("assets",[]):
        if a.get("path")==full:
            a["sha256"]=sha; a["status"]="MOTION_REPAIR_VERIFIED"; found=True
            note=f"2026-09-20 MOTION-006 exact approved pair {ph}; donor roots M003/M010 VERIFIED."
            if note not in a.setdefault("notes",[]): a["notes"].append(note)
    assert found,("manifest",full)
    found=False
    for k,v in inv.get("requiredFrames",{}).items():
        if v.get("path")==rel:
            v["sha256"]=sha; v["state"]="motion-repair-verified"
            v["motionRepairQa"]=str((WORK/f"bd_rd_{ph}_candidate_v1_qa.json").relative_to(ROOT)); found=True
    assert found,("inventory",rel)

e=next(v for v in amap.get("entries",[]) if v.get("actionKey")=="BD+RD:RF/R")
e["hitSha256"]=EXPECTED["hit"]; e["reboundSha256"]=EXPECTED["rebound"]
e["motionRepairQaStatus"]="EXACT_VISUAL_PASS_PROMOTED"
e["motionRepairMethod"]="neutral body + VERIFIED RD:R + VERIFIED BD:RF"

sa=x.setdefault("repairSpec",{}).setdefault("sourceAuthority",{})
sa["hitSha256"]=EXPECTED["hit"]; sa["reboundSha256"]=EXPECTED["rebound"]
x["status"]="FIXED_PENDING_RUNTIME_QA"; x["repairSpec"]["state"]="FIXED_PENDING_RUNTIME_QA"
x["updatedAt"]="2026-09-20T13:07:00+09:00"
progress="character-assets/edit-workspaces/motion-repair-20260920/front-m006/M006_RUNTIME_QA_STATE.json"
inv["runtimeQaTarget"]={"measureStart":130,"measureEnd":130,"actions":["BD+RD:RF/R"],"progressPath":progress,"blockKey":"M006-BD-RD"}
state={
 "schemaVersion":1,"issueId":"MOTION-006","actionKey":"BD+RD:RF/R",
 "status":"FORMAL_PROMOTED_RUNTIME_QA_PENDING",
 "exactCandidate":{"hitSha256":EXPECTED["hit"],"reboundSha256":EXPECTED["rebound"],"candidateRunId":35488049381,"candidateArtifactId":10598631500},
 "runtimeQaEvidence":{}
}
STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
backlog["updatedAt"]="2026-09-20T13:07:00+09:00"; amap["updatedAt"]="2026-09-20T13:07:00+09:00"
BP.write_text(json.dumps(backlog,ensure_ascii=False,indent=2)+"\n")
IP.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n")
AP.write_text(json.dumps(amap,ensure_ascii=False,indent=2)+"\n")
MP.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"promoted":True,"hit":EXPECTED["hit"],"rebound":EXPECTED["rebound"],"runtimeMeasure":130}))
