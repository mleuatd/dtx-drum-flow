#!/usr/bin/env python3
import hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m005"
EXPECTED={
 "hit":"8b1dcbf1d3287ee90bb4425380314fd412aeaeb407ccb1664815493f1cac6423",
 "rebound":"cd33610f79643b80222a250410eeaf2207be7d1014baa2f8847c9e611ba2ac6b",
}
FORMAL={
 "hit":ROOT/"character-assets/layers/character/combo/bd_hh_rf_r_hit_refresh.png",
 "rebound":ROOT/"character-assets/layers/character/combo/bd_hh_rf_r_rebound_refresh.png",
}
BP=ROOT/"character-assets/prototypes/luna_say_maybe_16m/MOTION_DEFECT_BACKLOG.json"
IP=ROOT/"character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json"
AP=ROOT/"character-assets/prototypes/luna_say_maybe_16m/ACTION_KEY_ASSET_MAP.json"
MP=ROOT/"character-assets/config/assets_manifest.json"
STATE=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m005/M005_RUNTIME_QA_STATE.json"

summary=json.loads((WORK/"M005_SUMMARY.json").read_text())
assert summary.get("pairMachinePass") is True, summary
by={x["phase"]:x for x in summary["phases"]}
for ph in ("hit","rebound"):
    assert by[ph]["candidateSha256"]==EXPECTED[ph], (ph,by[ph]["candidateSha256"])
    shutil.copyfile(ROOT/by[ph]["candidate"],FORMAL[ph])
    got=hashlib.sha256(FORMAL[ph].read_bytes()).hexdigest()
    assert got==EXPECTED[ph],(ph,got)

backlog=json.loads(BP.read_text()); inv=json.loads(IP.read_text()); amap=json.loads(AP.read_text()); manifest=json.loads(MP.read_text())
x=next(v for v in backlog["defects"] if v["issueId"]=="MOTION-005")
claim=x.get("claim") or {}
assert claim.get("owner")=="CHATGPT-FRONT" and claim.get("batch")=="FRONT-M005-AFTER-M007",claim
vq=x.get("visualIntegrityQa") or {}; ev=vq.get("reviewEvidence") or {}
assert vq.get("humanAnatomy")=="PASS" and vq.get("linework")=="PASS" and vq.get("fixedDrumComposite")=="PASS" and not vq.get("promotionBlocked")
assert ev.get("candidateHitSha256")==EXPECTED["hit"] and ev.get("candidateReboundSha256")==EXPECTED["rebound"]

paths={
 "hit":"character-assets/layers/character/combo/bd_hh_rf_r_hit_refresh.png",
 "rebound":"character-assets/layers/character/combo/bd_hh_rf_r_rebound_refresh.png",
}
for ph in ("hit","rebound"):
    full=paths[ph]; rel=full.replace("character-assets/","",1); sha=EXPECTED[ph]
    found=False
    for a in manifest.get("assets",[]):
        if a.get("path")==full:
            a["sha256"]=sha; a["status"]="MOTION_REPAIR_VERIFIED"; found=True
            note=f"2026-09-20 MOTION-005 exact approved pair {ph}; donor roots M003/M007 VERIFIED."
            if note not in a.setdefault("notes",[]): a["notes"].append(note)
    assert found,("manifest",full)
    found=False
    for k,v in inv.get("requiredFrames",{}).items():
        if v.get("path")==rel:
            v["sha256"]=sha; v["state"]="motion-repair-verified"
            v["motionRepairQa"]=str((WORK/f"bd_hh_{ph}_candidate_v1_qa.json").relative_to(ROOT)); found=True
    assert found,("inventory",rel)

e=next(v for v in amap.get("entries",[]) if v.get("actionKey")=="BD+HH:RF/R")
e["hitSha256"]=EXPECTED["hit"]; e["reboundSha256"]=EXPECTED["rebound"]
e["motionRepairQaStatus"]="EXACT_VISUAL_PASS_PROMOTED"
e["motionRepairMethod"]="neutral body + VERIFIED HH:R + VERIFIED BD:RF"

sa=x.setdefault("repairSpec",{}).setdefault("sourceAuthority",{})
sa["hitSha256"]=EXPECTED["hit"]; sa["reboundSha256"]=EXPECTED["rebound"]
x["status"]="FIXED_PENDING_RUNTIME_QA"; x["repairSpec"]["state"]="FIXED_PENDING_RUNTIME_QA"
x["updatedAt"]="2026-09-20T12:45:00+09:00"
evidence="M005 exact pair promoted after machine + visual PASS; runtime QA pending."
if evidence not in x.setdefault("evidence",[]): x["evidence"].append(evidence)

progress="character-assets/edit-workspaces/motion-repair-20260920/front-m005/M005_RUNTIME_QA_STATE.json"
inv["runtimeQaTarget"]={"measureStart":137,"measureEnd":137,"actions":["BD+HH:RF/R"],"progressPath":progress,"blockKey":"M005-BD-HH"}
state={
 "schemaVersion":1,"issueId":"MOTION-005","actionKey":"BD+HH:RF/R",
 "status":"FORMAL_PROMOTED_RUNTIME_QA_PENDING",
 "exactCandidate":{"hitSha256":EXPECTED["hit"],"reboundSha256":EXPECTED["rebound"],"candidateRunId":35487131337,"candidateArtifactId":10598475674},
 "runtimeQaEvidence":{}
}
STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
backlog["updatedAt"]="2026-09-20T12:45:00+09:00"; amap["updatedAt"]="2026-09-20T12:45:00+09:00"
BP.write_text(json.dumps(backlog,ensure_ascii=False,indent=2)+"\n")
IP.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n")
AP.write_text(json.dumps(amap,ensure_ascii=False,indent=2)+"\n")
MP.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"promoted":True,"hit":EXPECTED["hit"],"rebound":EXPECTED["rebound"],"runtimeMeasure":137}))
