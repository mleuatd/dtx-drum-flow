#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, os, shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
WORK=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front06"
BACKLOG=PROTO/"MOTION_DEFECT_BACKLOG.json"
MANIFEST=ROOT/"character-assets/config/assets_manifest.json"
INVENTORY=PROTO/"asset_inventory.json"
AMAP=PROTO/"ACTION_KEY_ASSET_MAP.json"
PREVAL=WORK/"FRONT06_PREPROMOTION_VALIDATION_V3.json"
STATIC=WORK/"FRONT06_STATIC_VISUAL_QA_V3.json"
RUNTIME=WORK/"FRONT06_RUNTIME_QA_V3.json"
RESULT=WORK/"FRONT06_PROMOTION_RESULT_V3.json"
FORMAL={
 "hit":ROOT/"character-assets/layers/character/combo/bd_rc_hit.png",
 "rebound":ROOT/"character-assets/layers/character/combo/bd_rc_rebound.png",
}
CAND={
 "hit":WORK/"bd_rc_hit_candidate_v3.png",
 "rebound":WORK/"bd_rc_rebound_candidate_v3.png",
}
REL={
 "hit":"character-assets/layers/character/combo/bd_rc_hit.png",
 "rebound":"character-assets/layers/character/combo/bd_rc_rebound.png",
}
def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path):
    return json.loads(p.read_text(encoding="utf-8"))
def dump(p:Path,d):
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def now_jst():
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")

backlog=load(BACKLOG)
defect=next(x for x in backlog["defects"] if x.get("issueId")=="MOTION-002")
claim=defect.get("claim") or {}
assert claim.get("state")=="CLAIMED" and claim.get("owner")=="CHATGPT-FRONT" and claim.get("batch")=="HOLD-REPAIR-FRONT-06", claim
assert defect.get("status")!="VERIFIED", "MOTION-002 already VERIFIED"

static=load(STATIC); runtime=load(RUNTIME); preval=load(PREVAL)
assert static.get("decision")=="STATIC_PAIR_PASS_RUNTIME_REQUIRED"
assert all(v.startswith("PASS") for k,v in static.get("gates",{}).items())
assert runtime["runtime"]["failed"]==0 and runtime["runtime"]["passed"]==8
assert runtime["visualRuntimeReview"]["pcHit"]=="PASS" and runtime["visualRuntimeReview"]["pcRebound"]=="PASS"
assert runtime["visualRuntimeReview"]["xperiaPortraitHit"]=="PASS" and runtime["visualRuntimeReview"]["xperiaPortraitRebound"]=="PASS"
assert preval.get("validation")=="PASS" and preval.get("characterAssetValidation")=="PASS" and preval.get("runtimePoseRegression")=="PASS"

before={k:sha(v) for k,v in FORMAL.items()}
assert before==preval["beforeFormalSha256"], {"formal_changed_since_validation":before,"validated":preval["beforeFormalSha256"]}
expected=preval["stagedCandidateSha256"]
for phase in ("hit","rebound"):
    assert sha(CAND[phase])==expected[phase], (phase,sha(CAND[phase]),expected[phase])
    shutil.copyfile(CAND[phase],FORMAL[phase])
after={k:sha(v) for k,v in FORMAL.items()}
assert after==expected

manifest=load(MANIFEST); inv=load(INVENTORY); amap=load(AMAP)
for phase in ("hit","rebound"):
    asset=next((x for x in manifest.get("assets",[]) if x.get("path")==REL[phase]),None)
    assert asset is not None, REL[phase]
    asset["sha256"]=after[phase]
    asset["status"]="MOTION_REPAIR_VERIFIED"
    notes=asset.setdefault("notes",[])
    note="2026-09-20 FRONT06 v3: static visual PASS, real-chart PC/Xperia PASS, prepromotion validation PASS."
    if note not in notes: notes.append(note)
    invrel=REL[phase].replace("character-assets/","",1)
    frames=[(fid,v) for fid,v in inv.get("requiredFrames",{}).items() if v.get("path")==invrel]
    assert frames, invrel
    for fid,frame in frames:
        frame["sha256"]=after[phase]
        frame["state"]="motion-repair-verified"
        frame["motionRepairQa"]=str(RUNTIME.relative_to(ROOT)).replace("\\","/")

entry=next((x for x in amap.get("entries",[]) if x.get("actionKey")=="BD+RC:RF/R"),None)
assert entry is not None
entry["hitSha256"]=after["hit"]; entry["reboundSha256"]=after["rebound"]
entry["motionRepairQaStatus"]="FRONT06_V3_VALIDATED_PROMOTED_PENDING_PUBLIC_RUNTIME"
entry["motionRepairMethod"]="neutral body + single RC arm replacement + BD/RF knee-to-boot transplant"
entry["motionRepairEvidence"]={
 "static":str(STATIC.relative_to(ROOT)).replace("\\","/"),
 "candidateRuntime":str(RUNTIME.relative_to(ROOT)).replace("\\","/"),
 "prepromotionValidation":str(PREVAL.relative_to(ROOT)).replace("\\","/")
}
amap["updatedAt"]=now_jst()

run_id=os.environ.get("GITHUB_RUN_ID","")
stamp=now_jst()
defect["status"]="PROMOTED_PENDING_PUBLIC_RUNTIME_QA"
defect["updatedAt"]=stamp
defect.setdefault("repairSpec",{})["state"]="PROMOTED_PENDING_PUBLIC_RUNTIME_QA"
defect["front06ValidatedPromotion"]={
 "candidateVersion":"v3",
 "oldFormalSha256":before,
 "newFormalSha256":after,
 "method":"neutral pelvis/thigh retained; destructive single RC-arm donor replacement; verified BD/RF knee-to-boot donor transplant",
 "staticQa":{"status":"PASS","evidence":str(STATIC.relative_to(ROOT)).replace("\\","/")},
 "candidateRuntimeQa":{"status":"PASS","runId":runtime["runtime"]["runId"],"artifactId":runtime["runtime"]["artifactId"],"measure":runtime["runtime"]["measure"],"viewports":runtime["runtime"]["viewports"]},
 "prepromotionValidation":{"status":"PASS","runId":preval["runId"],"artifactId":preval["artifactId"]},
 "promotionWorkflowRunId":run_id,
 "promotedAt":stamp,
 "publicRuntimeQa":"PENDING"
}
defect["latestVisualIntegrityQa"]={
 "humanAnatomy":"PASS","linework":"PASS","fixedDrumComposite":"PASS","hitReboundTransition":"PASS",
 "candidateRealChartRuntime":"PASS","pc":"PASS","xperiaPortrait":"PASS","validation":"PASS",
 "publicRuntime":"PENDING"
}
defect.setdefault("decisionLog",[]).append({
 "at":stamp,
 "decision":"FRONT06_V3_FORMAL_PROMOTED_PENDING_PUBLIC_RUNTIME",
 "detail":f"Promoted v3 only after static pair PASS, real-chart M103 PC/Xperia 8/8 PASS, and prepromotion validation PASS. Formal SHA hit={after['hit']} rebound={after['rebound']}. Claim retained until public Pages runtime confirmation."
})
backlog["updatedAt"]=stamp

preval["formalCommitted"]=True
preval["formalPromotionWorkflowRunId"]=run_id
preval["promotedFormalSha256"]=after
preval["promotedAt"]=stamp

result={
 "schemaVersion":1,"issueId":"MOTION-002","actionKey":"BD+RC:RF/R","claimBatch":"HOLD-REPAIR-FRONT-06",
 "oldFormalSha256":before,"newFormalSha256":after,"candidateVersion":"v3","promotionStatus":"PROMOTED_PENDING_PUBLIC_RUNTIME_QA",
 "promotionWorkflowRunId":run_id,"staticQa":"PASS","candidateRuntimeQa":"PASS","prepromotionValidation":"PASS","claimReleased":False
}
dump(MANIFEST,manifest); dump(INVENTORY,inv); dump(AMAP,amap); dump(BACKLOG,backlog); dump(PREVAL,preval); dump(RESULT,result)
print(json.dumps(result,ensure_ascii=False))
