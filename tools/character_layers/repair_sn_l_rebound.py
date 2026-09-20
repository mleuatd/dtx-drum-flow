#!/usr/bin/env python3
import hashlib, io, json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"character-assets/reference-models/luna_video_20260919/runtime_pose_constraints"
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920"
OUT.mkdir(parents=True,exist_ok=True)

HIT=ROOT/"character-assets/layers/character/sn/hit_l.png"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
DONOR_BLOB="f8e4c1fffe3b959f862b8039a08b30fb4c2cf8cd"
DONOR_SHA256="79484f0681273bb86b3ea9e56514cb9aa822945c6dc4b086d3e7093cbf25c777"

def blob_bytes(sha):
    test=subprocess.run(["git","cat-file","-e",sha],cwd=ROOT)
    if test.returncode:
        subprocess.run(["git","fetch","--unshallow","--no-tags","origin"],cwd=ROOT,check=False)
    return subprocess.check_output(["git","cat-file","blob",sha],cwd=ROOT)

raw=blob_bytes(DONOR_BLOB)
assert hashlib.sha256(raw).hexdigest()==DONOR_SHA256
donor=Image.open(io.BytesIO(raw)).convert("RGBA")
hit=Image.open(HIT).convert("RGBA")
drum=Image.open(DRUM).convert("RGBA")
assert hit.size==donor.size==drum.size==(1448,1086)
W,H=hit.size

hp=json.loads((BASE/"SN_L_hit_V1.json").read_text())
rp=json.loads((BASE/"SN_L_rebound_V1.json").read_text())

def pt(obj,key):
    return tuple(map(round,obj["joints"][key]))

h_elbow,h_wrist,h_tip=pt(hp,"elbow_l"),pt(hp,"wrist_l"),tuple(map(round,hp["stickTip"]))
r_elbow,r_wrist,r_tip=pt(rp,"elbow_l"),pt(rp,"wrist_l"),tuple(map(round,rp["stickTip"]))

# Source-bound semantic mask: active left forearm/hand + both old/new stick corridors only.
arm=Image.new("L",(W,H),0); d=ImageDraw.Draw(arm)
for a,b in [(h_elbow,h_wrist),(r_elbow,r_wrist)]:
    d.line([a,b],fill=255,width=112)
for p,r in [(h_elbow,58),(h_wrist,72),(r_elbow,58),(r_wrist,72)]:
    d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
arm_a=np.asarray(arm)>0
yy,xx=np.indices((H,W))
arm_a &= (yy>=430)

stick=Image.new("L",(W,H),0); s=ImageDraw.Draw(stick)
for a,b in [(h_wrist,h_tip),(r_wrist,r_tip)]:
    s.line([a,b],fill=255,width=42)
for p,r in [(h_wrist,34),(r_wrist,34),(h_tip,28),(r_tip,28)]:
    s.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
stick_a=np.asarray(stick)>0

allowed=arm_a|stick_a
# Static locks: never alter upper-hand/shoulder, head, pelvis/seat, legs, right side.
allowed &= (yy<570)&(xx<750)
allowed &= ~((yy<440)&(xx>=625))
# Tiny diagnosed floating-fragment cleanup below/left of rebound tip.
allowed[432:482,385:442]=True

hit_a=np.asarray(hit)
don_a=np.asarray(donor)
candidate=hit.copy()
mask=Image.fromarray((allowed.astype(np.uint8)*255),"L")
candidate.paste(donor,(0,0),mask)

# In the tiny cleanup zone, only donor-transparent pixels may erase residue.
ca=np.asarray(candidate).copy()
zone=np.zeros((H,W),dtype=bool); zone[432:482,385:442]=True
clear=zone&(don_a[:,:,3]==0)
ca[clear]=0
candidate=Image.fromarray(ca,"RGBA")

CAND=OUT/"sn_l_rebound_candidate_v14.png"
COMP=OUT/"sn_l_rebound_candidate_v14_fixed_drum.png"
QA=OUT/"sn_l_rebound_candidate_v14_qa.json"
candidate.save(CAND)
Image.alpha_composite(drum,candidate).save(COMP)

q=np.asarray(candidate)
changed=np.any(q!=hit_a,axis=2)
outside=int(np.count_nonzero(changed&~allowed))
ys,xs=np.where(changed)
bbox=None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]

guards={
 "head":(500,0,430,320),
 "upper_hand_shoulder":(625,320,125,120),
 "pelvis_seat":(560,570,500,260),
 "legs_stool":(300,700,900,386),
}
gc={}
for name,(x,y,w,h) in guards.items():
    gc[name]=int(np.count_nonzero(np.any(q[y:y+h,x:x+w]!=hit_a[y:y+h,x:x+w],axis=2)))

hard={
 "canvas":candidate.size==(1448,1086),
 "alpha":candidate.getchannel("A").getextrema()==(0,255),
 "outsideAllowedChangedPixels":outside==0,
 "headExactToHit":gc["head"]==0,
 "upperHandShoulderExactToHit":gc["upper_hand_shoulder"]==0,
 "pelvisSeatExactToHit":gc["pelvis_seat"]==0,
 "legsStoolExactToHit":gc["legs_stool"]==0,
 "sourceBoundDonor":hashlib.sha256(raw).hexdigest()==DONOR_SHA256,
}
report={
 "schemaVersion":14,
 "issueId":"MOTION-001","actionKey":"SN:L","phase":"rebound",
 "candidate":str(CAND.relative_to(ROOT)),
 "method":"formal hit static parent + exact clean rebound source blob; narrow left forearm/hand/stick semantic replacement only",
 "source":{"cleanReboundBlob":DONOR_BLOB,"cleanReboundSha256":DONOR_SHA256,
           "hitSha256":hashlib.sha256(HIT.read_bytes()).hexdigest()},
 "changedRoi":{"changedPixelsVsHit":int(changed.sum()),"changedBBoxVsHit":bbox,
               "outsideAllowedChangedPixels":outside,"floatingCleanupPixels":int(clear.sum())},
 "guardChangedPixelsVsHit":gc,
 "hardPass":hard,
}
report["pass"]=all(hard.values()) and int(changed.sum())>=250
QA.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report,ensure_ascii=False))
if not report["pass"]:
    raise SystemExit(2)
