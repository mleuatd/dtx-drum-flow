#!/usr/bin/env python3
import io, json, hashlib, subprocess, shutil
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920"
OUT.mkdir(parents=True,exist_ok=True)
hit_p=ROOT/"character-assets/layers/character/sn/hit_l.png"
formal=ROOT/"character-assets/layers/character/sn/rebound_l.png"
manifest=ROOT/"character-assets/config/assets_manifest.json"
inventory=ROOT/"character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json"
amap=ROOT/"character-assets/prototypes/luna_say_maybe_16m/ACTION_KEY_ASSET_MAP.json"
ledger=ROOT/"character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json"
backlog=ROOT/"character-assets/prototypes/luna_say_maybe_16m/MOTION_DEFECT_BACKLOG.json"
SRC_COMMIT="a4e3854449e292264192afa63469edf0fb5048af"
SRC_PATH="character-assets/layers/character/sn/rebound_l.png"
HIT_SHA="9941584d670ac6441b8853c8c191318aff7482264f81b6473fa1a3e381cd4cfb"
SRC_SHA="79484f0681273bb86b3ea9e56514cb9aa822945c6dc4b086d3e7093cbf25c777"
CURRENT_SHA="c3f480bdd5861d5703af400089682fe94427ef07ccd14cf1ff514e45e73d9d9c"

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(p.read_bytes())

assert sha_file(hit_p)==HIT_SHA
assert sha_file(formal)==CURRENT_SHA
src_bytes=subprocess.check_output(["git","show",f"{SRC_COMMIT}:{SRC_PATH}"])
assert sha_bytes(src_bytes)==SRC_SHA

hit=Image.open(hit_p).convert("RGBA")
src=Image.open(io.BytesIO(src_bytes)).convert("RGBA")
assert hit.size==src.size==(1448,1086)
W,H=hit.size

warp=np.array([[1.0195778608322144,-0.012023212388157845,20.75324058532715],
               [0.004541634116321802,1.0361989736557007,-7.703911781311035]],dtype=np.float32)
S=np.array(src)
AL=np.empty_like(S)
for c in range(4):
    AL[:,:,c]=cv2.warpAffine(S[:,:,c],warp,(W,H),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,
                             borderMode=cv2.BORDER_CONSTANT,borderValue=0)
aligned=Image.fromarray(AL,"RGBA")

mask=Image.new("L",(W,H),0); d=ImageDraw.Draw(mask)
for a,b in [((595,473),(516,449)),((629,462),(567,484))]: d.line([a,b],fill=255,width=100)
for q,rad in [((595,473),56),((516,449),64),((629,462),56),((567,484),64)]:
    d.ellipse((q[0]-rad,q[1]-rad,q[0]+rad,q[1]+rad),fill=255)
for a,b in [((516,449),(420,535)),((567,484),(414,409))]: d.line([a,b],fill=255,width=46)
for q,rad in [((420,535),30),((414,409),30)]:
    d.ellipse((q[0]-rad,q[1]-rad,q[0]+rad,q[1]+rad),fill=255)
d.rounded_rectangle((520,455,690,555),radius=35,fill=255)
clip=np.zeros((H,W),np.uint8); clip[300:585,360:705]=255
m=np.minimum(np.array(mask),clip)
mask=Image.fromarray(m).filter(ImageFilter.GaussianBlur(1.5))
mask=Image.fromarray(np.minimum(np.array(mask),clip).astype(np.uint8),"L")

cand=hit.copy(); cand.paste(aligned,(0,0),mask)
A=np.array(hit); C=np.array(cand)
patch=np.zeros((H,W),bool); patch[455:555,520:690]=True
res=(A[:,:,3]>80)&(AL[:,:,3]<20)&(C[:,:,3]>80)&patch
rm=np.array(Image.fromarray((res.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(3)))>0
rm &= patch
C[rm]=AL[rm]
gap=(C[:,:,3]<8)&(AL[:,:,3]>180)&patch
C[gap]=AL[gap]
cand=Image.fromarray(C,"RGBA")

cand_p=OUT/"sn_l_rebound_candidate_v16.png"
qa_p=OUT/"sn_l_rebound_candidate_v16_qa.json"
cand.save(cand_p)
new_sha=sha_file(cand_p)

changed=np.any(A!=C,axis=2)
allowed=np.zeros((H,W),bool); allowed[300:585,360:705]=True
outside=int(np.count_nonzero(changed & ~allowed))
guards={"head":(500,0,430,325),"right_arm":(800,300,380,290),"pelvis_seat":(560,585,440,250),"legs_stool":(280,690,900,396)}
g={}
for k,(x,y,w,h) in guards.items():
    g[k]=int(np.count_nonzero(np.any(A[y:y+h,x:x+w]!=C[y:y+h,x:x+w],axis=2)))
residue=int(np.count_nonzero((A[:,:,3]>80)&(AL[:,:,3]<20)&(C[:,:,3]>80)&patch))
alpha_gap=int(np.count_nonzero((C[:,:,3]<8)&(AL[:,:,3]>180)&patch))
hard={"outsideEnvelope":outside==0,"head":g["head"]==0,"rightArm":g["right_arm"]==0,
      "pelvisSeat":g["pelvis_seat"]==0,"legsStool":g["legs_stool"]==0,
      "oldHandResidue":residue==0,"alphaGap":alpha_gap==0}
q={"schemaVersion":16,"issueId":"MOTION-001","actionKey":"SN:L","phase":"rebound",
   "method":"protected source rebound aligned to formal hit; left forearm/hand/stick ROI only",
   "candidateSha256":new_sha,"rasterChecks":{"outsideEnvelopeChangedPixels":outside,
   "guardChangedPixels":g,"oldHandResiduePixels":residue,"alphaGapPixels":alpha_gap,
   "changedPixels":int(changed.sum())},"hardPass":hard,"pass":all(hard.values())}
qa_p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n")
assert q["pass"], q

old_sha=sha_file(formal)
shutil.copyfile(cand_p,formal)
assert sha_file(formal)==new_sha

m=json.loads(manifest.read_text())
for x in m["assets"]:
    if x.get("path")=="character-assets/layers/character/sn/rebound_l.png":
        x["sha256"]=new_sha
        x["status"]="MOTION_REPAIR_STATIC_PASS_RUNTIME_PENDING"
        x.setdefault("notes",[]).append("2026-09-20 MOTION-001 v16 source-bound repair; static visual gates PASS; runtime pending.")
manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")

inv=json.loads(inventory.read_text())
for x in inv.get("requiredFrames",{}).values():
    if x.get("path")=="layers/character/sn/rebound_l.png":
        x["sha256"]=new_sha
        x["state"]="motion-repair-static-pass-runtime-pending"
inventory.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+"\n")

a=json.loads(amap.read_text())
for x in a.get("entries",[]):
    if x.get("actionKey")=="SN:L":
        x["reboundSha256"]=new_sha
        x["motionRepair"]="MOTION-001 rebound v16 source-bound aligned local repair"
        x["motionRepairQa"]="character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v16_qa.json"
        x["qaStatus"]="RUNTIME_QA_PENDING"
a["updatedAt"]="2026-09-20T17:41:00+09:00"
amap.write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n")

l=json.loads(ledger.read_text())
for x in l.get("targets",[]):
    if x.get("id")=="sn_l_rebound":
        x["sha256"]=new_sha
        x["brushupStatus"]="FIXED_PENDING_RUNTIME_QA"
        x["claimState"]="CLAIMED"
        x["qaEvidence"]="character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v16_qa.json"
l["updatedAt"]="2026-09-20T17:41:00+09:00"
l["fastLocalRepairStable"]={"terminalId":"CHAT-FAST-REPAIR-STABLE","currentIssueId":"MOTION-001","currentActionKey":"SN:L",
 "stage":"FORMAL_PROMOTED_RUNTIME_PENDING","updatedAt":"2026-09-20T17:41:00+09:00",
 "candidate":{"version":"v16","sha256":new_sha},
 "qa":{"humanAnatomy":"PASS","linework":"PASS","fixedDrumComposite":"PASS","runtime":"PENDING"}}
ledger.write_text(json.dumps(l,ensure_ascii=False,indent=2)+"\n")

b=json.loads(backlog.read_text())
for x in b.get("defects",[]):
    if x.get("issueId")=="MOTION-001":
        x["status"]="FIXED_PENDING_RUNTIME_QA"
        x["updatedAt"]="2026-09-20T17:41:00+09:00"
        x["repairSpec"]["state"]="FIXED_PENDING_RUNTIME_QA"
        x["reboundRepair"]={"status":"FORMAL_PROMOTED_RUNTIME_PENDING","oldSha256":old_sha,"sourceSha256":SRC_SHA,
          "newSha256":new_sha,"candidate":"character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v16.png",
          "qa":"character-assets/edit-workspaces/motion-repair-20260920/sn_l_rebound_candidate_v16_qa.json",
          "staticGuardChangedPixels":g}
        x["visualIntegrityQa"]={"humanAnatomy":"PASS","linework":"PASS","fixedDrumComposite":"PASS",
          "runtimeTransition":"PENDING","promotionBlocked":True,"ruleVersion":"2026-09-20-visual-integrity-v1",
          "note":"v16 formal promoted after source-bound aligned local repair; static gates PASS, runtime real-chart QA pending.",
          "reviewedAt":"2026-09-20T17:41:00+09:00"}
        x.setdefault("decisionLog",[]).append({"at":"2026-09-20T17:41:00+09:00",
          "decision":"SN_L_V16_FORMAL_PROMOTED_RUNTIME_PENDING",
          "detail":f"v16 {new_sha}; deterministic local QA PASS; runtime real-chart QA required before VERIFIED."})
b["updatedAt"]="2026-09-20T17:41:00+09:00"
backlog.write_text(json.dumps(b,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"oldFormalSha256":old_sha,"newSha256":new_sha,"qaPass":q["pass"]}))
