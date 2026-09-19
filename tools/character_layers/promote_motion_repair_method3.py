#!/usr/bin/env python3
import json, hashlib, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
WORK=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/method3"
summary_path=WORK/"METHOD3_CANDIDATE_SUMMARY.json"
manifest_path=ROOT/"character-assets/config/assets_manifest.json"
inventory_path=PROTO/"asset_inventory.json"
amap_path=PROTO/"ACTION_KEY_ASSET_MAP.json"
ledger_path=ROOT/"character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json"
backlog_path=PROTO/"MOTION_DEFECT_BACKLOG.json"

if not summary_path.exists():
    print("No candidate summary yet; nothing to promote.")
    raise SystemExit(0)

summary=json.loads(summary_path.read_text())
manifest=json.loads(manifest_path.read_text())
inventory=json.loads(inventory_path.read_text())
amap=json.loads(amap_path.read_text())
ledger=json.loads(ledger_path.read_text())
backlog=json.loads(backlog_path.read_text())

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def inv_rel(formal):
    return formal.replace("character-assets/","",1)

promoted=[]; skipped=[]; failed_candidates=[]
for rec in summary.get("targets",[]):
    tid=rec["id"]
    t=next((x for x in ledger.get("targets",[]) if x.get("id")==tid),None)
    if not t:
        skipped.append({"id":tid,"reason":"ledger_target_missing"}); continue
    if t.get("claimState")=="COMPLETED":
        skipped.append({"id":tid,"reason":"already_completed"}); continue
    if t.get("terminalId")!="CHAT-MOTION-REPAIR":
        skipped.append({"id":tid,"reason":"claim_owner_changed"}); continue
    if not rec.get("pass"):
        t["brushupStatus"]="AUTO_REPAIR_METHOD3_FAIL"
        t["qaEvidence"]=str((WORK/(tid.lower()+"_qa.json")).relative_to(ROOT)) if (WORK/(tid.lower()+"_qa.json")).exists() else None
        failed_candidates.append({"id":tid,"actionKey":rec["actionKey"],"phase":rec["phase"],"checks":rec.get("checks"),"changedRatioVsNeutral":rec.get("changedRatioVsNeutral")})
        continue
    formal_rel=t["formalGitHubPath"]; formal=ROOT/formal_rel
    current=sha(formal)
    if current!=rec["sourceSha256"]:
        t["brushupStatus"]="AUTO_REPAIR_STALE_SOURCE_RECHECK"
        skipped.append({"id":tid,"reason":"source_sha_changed","expected":rec["sourceSha256"],"current":current})
        continue
    cand=ROOT/rec["candidate"]
    shutil.copyfile(cand,formal)
    newsha=sha(formal)

    # Manifest exact full path.
    found=False
    for a in manifest.get("assets",[]):
        if a.get("path")==formal_rel:
            a["sha256"]=newsha
            a["status"]="MOTION_REPAIR_VERIFIED"
            a.setdefault("notes",[]).append(f"2026-09-20 deterministic motion repair {rec['actionKey']} {rec['phase']}; auto candidate QA PASS.")
            found=True
    if not found: raise RuntimeError(f"manifest asset not found: {formal_rel}")

    # Inventory by normalized path.
    rel=inv_rel(formal_rel)
    inv_found=False
    for k,v in inventory.get("requiredFrames",{}).items():
        if v.get("path")==rel:
            v["sha256"]=newsha
            v["state"]="motion-repair-verified"
            v["motionRepairQa"]=str((WORK/(tid.lower()+"_qa.json")).relative_to(ROOT)) if (WORK/(tid.lower()+"_qa.json")).exists() else None
            inv_found=True
    if not inv_found:
        # Some runtime entries may not be in requiredFrames under the same key; record but do not silently fail.
        skipped.append({"id":tid,"reason":"inventory_path_not_found_but_manifest_updated","path":rel})

    # Action map.
    e=next((x for x in amap.get("entries",[]) if x.get("actionKey")==rec["actionKey"]),None)
    if e:
        field="hitSha256" if rec["phase"]=="hit" else "reboundSha256"
        e[field]=newsha
        e["motionRepairQaStatus"]="AUTO_CANDIDATE_PASS_PROMOTED"
        e["motionRepairLastPhase"]=rec["phase"]
        e["motionRepairMethod"]="method3: instrument-side forearm/stick corridor + neutral core lock"

    t["sha256"]=newsha
    t["brushupStatus"]="MOTION_REPAIR_VERIFIED"
    t["claimState"]="COMPLETED"
    t["completedAt"]="2026-09-20T05:45:00+09:00"
    t["qaEvidence"]=str((WORK/(tid.lower()+"_qa.json")).relative_to(ROOT)) if (WORK/(tid.lower()+"_qa.json")).exists() else None
    t["motionRepairChangedRatioVsNeutral"]=rec["changedRatioVsNeutral"]
    promoted.append({"id":tid,"actionKey":rec["actionKey"],"phase":rec["phase"],"oldSha256":current,"newSha256":newsha,"changedRatioVsNeutral":rec["changedRatioVsNeutral"]})

# Backlog per action status.
by_action={}
for p in promoted: by_action.setdefault(p["actionKey"],[]).append(p)
for d in backlog.get("defects",[]):
    key=d.get("actionKey")
    p=by_action.get(key,[])
    relevant=[r for r in summary.get("targets",[]) if r.get("actionKey")==key]
    if p:
        d["autoRepairPromotion"]={"promoted":p,"method":"method3: instrument-side forearm/stick corridor + neutral core lock","candidateSummary":str(summary_path.relative_to(ROOT))}
        phases={x["phase"] for x in p}
        if {"hit","rebound"}.issubset(phases):
            d["status"]="FIXED_PENDING_RUNTIME_QA"
            d["repairSpec"]["state"]="FIXED_PENDING_QA"
        else:
            d["status"]="IN_FIX"
            d["repairSpec"]["state"]="IN_FIX"
        d["updatedAt"]="2026-09-20T05:45:00+09:00"
    elif relevant and any(not r.get("pass") for r in relevant):
        d["status"]="AUTO_REPAIR_METHOD4_REQUIRED"
        d["repairSpec"]["state"]="IN_FIX"
        d["updatedAt"]="2026-09-20T05:45:00+09:00"

manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
inventory_path.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+"\n")
amap["updatedAt"]="2026-09-20T05:45:00+09:00"
amap_path.write_text(json.dumps(amap,ensure_ascii=False,indent=2)+"\n")
ledger["updatedAt"]="2026-09-20T05:45:00+09:00"
ledger_path.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
backlog["updatedAt"]="2026-09-20T05:45:00+09:00"
backlog_path.write_text(json.dumps(backlog,ensure_ascii=False,indent=2)+"\n")
record={"schemaVersion":1,"promoted":promoted,"failedCandidates":failed_candidates,"skipped":skipped}
(WORK/"METHOD3_PROMOTION_RESULT.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"promoted":len(promoted),"failedCandidates":len(failed_candidates),"skipped":len(skipped)}))
