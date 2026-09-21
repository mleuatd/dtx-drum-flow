#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
TRIAL=ROOT/"character-assets/generation-trials/dmr009-neutral-skeleton-v1"
CAND=TRIAL/"DMR009_bd_hh_rf_r_hit_candidate_neutral_skeleton_v1.png"
QA=TRIAL/"dmr009_attempt_20260921_v4_neutral_skeleton.json"
VQA=TRIAL/"DMR009_visual_qa_v2.json"
WORK=ROOT/"character-assets/CURRENT_WORK_ORDER.json"
STATUS=ROOT/"character-assets/versions/one-by-one-qa/CURRENT_STATUS.json"
TARGET=ROOT/"character-assets/layers/character/combo/bd_hh_rf_r_hit_refresh.png"
REBOUND=ROOT/"character-assets/layers/character/combo/bd_hh_rf_r_rebound_refresh.png"
BD=ROOT/"character-assets/layers/character/bd/hit_rf.png"
MANIFEST=ROOT/"character-assets/config/assets_manifest.json"
INVENTORY=ROOT/"character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json"
AMAP=ROOT/"character-assets/prototypes/luna_say_maybe_16m/ACTION_KEY_ASSET_MAP.json"
RESULT=TRIAL/"DMR009_PROMOTION_RESULT.json"

EXPECTED="8b84db012f41efabf2e7a3832c14b04938d34e2b58a1b6775f77a6849fa6d16c"
EXPECTED_BD="eb6935313168f29f8f804bb4b7e2f4aeb4896172b326411e01476975de3e3eb8"

def sha(p:Path)->str:
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def sync_manifest(manifest, path, newsha, note):
    rec=next((a for a in manifest.get("assets",[]) if a.get("path")==path),None)
    if not rec: raise SystemExit(f"manifest entry missing: {path}")
    rec["sha256"]=newsha
    rec["status"]="MOTION_REPAIR_VERIFIED"
    notes=rec.setdefault("notes",[])
    if note not in notes: notes.append(note)

def sync_inventory(inventory, relpath, newsha, state="motion-repair-verified"):
    found=False
    for _,frame in inventory.get("requiredFrames",{}).items():
        if frame.get("path")==relpath:
            frame["sha256"]=newsha
            frame["state"]=state
            found=True
    if not found: raise SystemExit(f"inventory frame missing: {relpath}")

def sync_action_map(amap, action, newsha, method):
    rec=next((x for x in amap.get("entries",[]) if x.get("actionKey")==action),None)
    if not rec: raise SystemExit(f"action map missing: {action}")
    rec["hitSha256"]=newsha
    rec["motionRepairQaStatus"]="EXACT_VISUAL_PASS_PROMOTED"
    rec["motionRepairLastPhase"]="hit"
    rec["motionRepairMethod"]=method

def main():
    work=json.loads(WORK.read_text(encoding="utf-8"))
    qa=json.loads(QA.read_text(encoding="utf-8"))
    vqa=json.loads(VQA.read_text(encoding="utf-8"))
    status=json.loads(STATUS.read_text(encoding="utf-8"))
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    inventory=json.loads(INVENTORY.read_text(encoding="utf-8"))
    amap=json.loads(AMAP.read_text(encoding="utf-8"))

    if work["issue"]["id"]!="DMR-009" or work["issue"]["phase"]!="hit":
        raise SystemExit("active work order is not DMR-009 hit")
    if work["issue"]["pairedAsset"]["allowModification"]:
        raise SystemExit("paired rebound must remain read-only")

    csha=sha(CAND)
    if csha!=EXPECTED: raise SystemExit(f"candidate SHA mismatch {csha}")
    if qa["candidate"]["sha256"]!=EXPECTED or qa["visualQa"]["status"]!="PASS":
        raise SystemExit("numeric QA does not authorize exact candidate")
    if qa["anatomy"]["result"]!="PASS" or qa["stick"]["result"]!="PASS" or qa["transition"]["result"]!="PASS":
        raise SystemExit("required numeric/transition gate failed")
    if vqa["candidateSha256"]!=EXPECTED or vqa["result"]!="PASS":
        raise SystemExit("visual QA does not authorize exact candidate")

    # Pre-existing metadata drift from the audited 008 BD repair is safe to
    # reconcile only if the current formal PNG exactly matches its documented
    # repaired SHA. Never change the BD image in this DMR-009 promotion.
    bd_actual=sha(BD)
    if bd_actual!=EXPECTED_BD:
        raise SystemExit(f"unexpected BD formal SHA; refusing unrelated metadata rewrite: {bd_actual}")

    rebound_before=sha(REBOUND)
    old_target_sha=sha(TARGET)

    shutil.copyfile(CAND,TARGET)
    promoted_sha=sha(TARGET)
    rebound_after=sha(REBOUND)
    if promoted_sha!=EXPECTED: raise SystemExit("formal copy SHA mismatch")
    if rebound_before!=rebound_after: raise SystemExit("READ_ONLY rebound changed")

    sync_manifest(
        manifest,
        "character-assets/layers/character/combo/bd_hh_rf_r_hit_refresh.png",
        promoted_sha,
        "2026-09-21 DMR-009 exact candidate promoted after numeric + AI visual + transition PASS."
    )
    sync_inventory(inventory,"layers/character/combo/bd_hh_rf_r_hit_refresh.png",promoted_sha)
    sync_action_map(amap,"BD+HH:RF/R",promoted_sha,"DMR-009 exact validated donor/bone-local hit promotion")

    # Metadata-only reconciliation for the already-formal audited 008 repair.
    sync_manifest(
        manifest,
        "character-assets/layers/character/bd/hit_rf.png",
        bd_actual,
        "2026-09-21 metadata reconciled to documented 008 repaired formal SHA; image unchanged."
    )
    sync_inventory(inventory,"layers/character/bd/hit_rf.png",bd_actual)
    sync_action_map(amap,"BD:RF",bd_actual,"metadata reconciliation to audited 008 repaired formal image; image unchanged")

    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    INVENTORY.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    amap["updatedAt"]="2026-09-21T23:20:00+09:00"
    AMAP.write_text(json.dumps(amap,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    status["updatedAt"]="2026-09-21T23:20:00+09:00"
    status["executionMode"]="ONE_IMAGE_ONLY_VERIFIED"
    status["activeWork"]["finalStatus"]="VERIFIED"
    status["activeWork"]["promotionBlocked"]=False
    status["activeWork"]["formalPath"]="character-assets/layers/character/combo/bd_hh_rf_r_hit_refresh.png"
    status["activeWork"]["formalSha256"]=promoted_sha
    status["resultSummary"]["formalImageOverwritten"]=True
    status["resultSummary"]["visualQaPassed"]=True
    status["resultSummary"]["transitionPassed"]=True
    status["resultSummary"]["verified"]=True
    status["nextAction"]="DMR-009 hit VERIFIED. Paired rebound remained read-only. Do not advance automatically."
    STATUS.write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    work["status"]="VERIFIED"
    work["completion"]={
      "state":"VERIFIED",
      "candidateSha256":EXPECTED,
      "formalPath":"character-assets/layers/character/combo/bd_hh_rf_r_hit_refresh.png",
      "formalSha256":promoted_sha,
      "pairedReboundModified":False,
      "note":"Exact numeric+AI-visual+transition PASS candidate promoted only after SHA lock and repository validation."
    }
    WORK.write_text(json.dumps(work,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    result={
      "schemaVersion":1,"issueId":"DMR-009","phase":"hit","result":"VERIFIED",
      "candidateSha256":EXPECTED,"previousFormalSha256":old_target_sha,
      "formalPath":"character-assets/layers/character/combo/bd_hh_rf_r_hit_refresh.png",
      "formalSha256":promoted_sha,"pairedReboundSha256":rebound_after,
      "pairedReboundModified":False,"numericQa":"PASS","aiVisualQa":"PASS","transitionQa":"PASS",
      "metadataReconciliation":{
        "bdRfImageChanged":False,
        "bdRfFormalSha256":bd_actual,
        "reason":"008 repaired PNG was already formal on main but manifest/inventory/action-map still referenced its pre-repair SHA."
      }
    }
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":
    main()
