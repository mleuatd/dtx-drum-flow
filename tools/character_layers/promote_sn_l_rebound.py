#!/usr/bin/env python3
import json, hashlib, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
candidate=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v2.png"
qa=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v2_qa.json"
formal=ROOT/"character-assets/layers/character/sn/rebound_l.png"
manifest=ROOT/"character-assets/config/assets_manifest.json"
inventory=ROOT/"character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json"
amap=ROOT/"character-assets/prototypes/luna_say_maybe_16m/ACTION_KEY_ASSET_MAP.json"
ledger=ROOT/"character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json"
backlog=ROOT/"character-assets/prototypes/luna_say_maybe_16m/MOTION_DEFECT_BACKLOG.json"

q=json.loads(qa.read_text())
assert q.get("pass") is True
assert all(q["hardPass"].values())
old_sha=hashlib.sha256(formal.read_bytes()).hexdigest()
assert old_sha=="79484f0681273bb86b3ea9e56514cb9aa822945c6dc4b086d3e7093cbf25c777"
shutil.copyfile(candidate,formal)
new_sha=hashlib.sha256(formal.read_bytes()).hexdigest()

m=json.loads(manifest.read_text())
for a in m["assets"]:
    if a.get("path")=="character-assets/layers/character/sn/rebound_l.png":
        a["sha256"]=new_sha
        a["status"]="MOTION_REPAIR_VERIFIED"
        a.setdefault("notes",[]).append("2026-09-20 MOTION-001 deterministic neutral-locked rebound repair; candidate v2 machine QA PASS.")
manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")

inv=json.loads(inventory.read_text())
for v in inv.get("requiredFrames",{}).values():
    if v.get("path")=="layers/character/sn/rebound_l.png":
        v["sha256"]=new_sha
        v["state"]="motion-repair-verified"
inventory.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n")

a=json.loads(amap.read_text())
for e in a.get("entries",[]):
    if e.get("actionKey")=="SN:L":
        e["reboundSha256"]=new_sha
        e["motionRepair"]="MOTION-001 rebound deterministic neutral-lock v2"
        e["motionRepairQa"]="character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v2_qa.json"
a["updatedAt"]="2026-09-20T05:31:00+09:00"
amap.write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n")

l=json.loads(ledger.read_text())
for t in l.get("targets",[]):
    if t.get("id")=="sn_l_rebound":
        t["sha256"]=new_sha
        t["brushupStatus"]="MOTION_REPAIR_VERIFIED"
        t["claimState"]="COMPLETED"
        t["completedAt"]="2026-09-20T05:31:00+09:00"
        t["qaEvidence"]="character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v2_qa.json"
l["updatedAt"]="2026-09-20T05:31:00+09:00"
ledger.write_text(json.dumps(l,ensure_ascii=False,indent=2)+"\n")

b=json.loads(backlog.read_text())
for d in b.get("defects",[]):
    if d.get("issueId")=="MOTION-001":
        d["status"]="PARTIAL_FIXED_HIT_CLAIMED_ELSEWHERE"
        d["updatedAt"]="2026-09-20T05:31:00+09:00"
        d["reboundRepair"]={"status":"VERIFIED_PROMOTED","oldSha256":old_sha,"newSha256":new_sha,"candidate":"character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v2.png","qa":"character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v2_qa.json","changedRatioVsNeutral":q["rasterChecks"]["changedRatioVsNeutral"],"staticGuardChangedPixels":q["rasterChecks"]["guardChangedPixels"]}
        d["repairSpec"]["state"]="IN_FIX"
b["updatedAt"]="2026-09-20T05:31:00+09:00"
backlog.write_text(json.dumps(b,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"oldSha256":old_sha,"newSha256":new_sha}))
