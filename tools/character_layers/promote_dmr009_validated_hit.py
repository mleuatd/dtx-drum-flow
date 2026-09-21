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
RESULT=TRIAL/"DMR009_PROMOTION_RESULT.json"
EXPECTED="8b84db012f41efabf2e7a3832c14b04938d34e2b58a1b6775f77a6849fa6d16c"

def sha(p:Path)->str:
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def main():
    work=json.loads(WORK.read_text(encoding="utf-8"))
    qa=json.loads(QA.read_text(encoding="utf-8"))
    vqa=json.loads(VQA.read_text(encoding="utf-8"))
    status=json.loads(STATUS.read_text(encoding="utf-8"))
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
    rebound_before=sha(REBOUND)
    old_target_sha=sha(TARGET)
    shutil.copyfile(CAND,TARGET)
    promoted_sha=sha(TARGET)
    rebound_after=sha(REBOUND)
    if promoted_sha!=EXPECTED: raise SystemExit("formal copy SHA mismatch")
    if rebound_before!=rebound_after: raise SystemExit("READ_ONLY rebound changed")

    status["updatedAt"]="2026-09-21T23:10:00+09:00"
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
      "pairedReboundModified":False,"numericQa":"PASS","aiVisualQa":"PASS","transitionQa":"PASS"
    }
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":
    main()
