#!/usr/bin/env python3
import json, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"character-assets/reference-models/luna_video_20260919"
PROTO=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
OUTDIR=ROOT/"character-assets/edit-workspaces/motion-repair-20260920"
OUTDIR.mkdir(parents=True,exist_ok=True)

neutral_path=ROOT/"character-assets/layers/character/base/neutral.png"
source_path=ROOT/"character-assets/layers/character/sn/rebound_l.png"
constraint_path=BASE/"runtime_pose_constraints/SN_L_rebound_V1.json"
neutral_constraint_path=BASE/"runtime_pose_constraints/SN_L_neutral_V1.json"
hit_constraint_path=BASE/"runtime_pose_constraints/SN_L_hit_V1.json"
drum_path=ROOT/"character-assets/layers/drum/drum_base.png"

neutral=Image.open(neutral_path).convert("RGBA")
source=Image.open(source_path).convert("RGBA")
drum=Image.open(drum_path).convert("RGBA")
c=json.loads(constraint_path.read_text())
neutral_pose=json.loads(neutral_constraint_path.read_text())
hit=json.loads(hit_constraint_path.read_text())
W,H=neutral.size
assert neutral.size==source.size==(1448,1086)

# Active-left-limb semantic corridor from tool-authority joints/effectors.
j=c["joints"]
shoulder=tuple(map(round,j["shoulder_l"]))
elbow=tuple(map(round,j["elbow_l"]))
wrist=tuple(map(round,j["wrist_l"]))
tip=tuple(map(round,c["stickTip"]))
hit_tip=tuple(map(round,hit["stickTip"]))

mask=Image.new("L",(W,H),0)
d=ImageDraw.Draw(mask)
# Wide enough to preserve actual drawn arm/clothing/stick, but deliberately local.
d.line([shoulder,elbow,wrist],fill=255,width=150,joint="curve")
for p,r in [(shoulder,85),(elbow,85),(wrist,75)]:
    d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
# Stick corridor follows wrist->source rebound stick tip.
d.line([wrist,tip],fill=255,width=38)
for p,r in [(tip,26),(hit_tip,18)]:
    d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)

# Also cover the approved-neutral LEFT arm/hand/stick pose. The candidate base
# is neutral, so any neutral pixels from the old left-arm pose must be inside
# the replace mask; otherwise they remain beside the rebound limb and create
# a false third hand/stick. Source transparency is allowed to erase them.
nj=neutral_pose["joints"]
n_shoulder=tuple(map(round,nj["shoulder_l"]))
n_elbow=tuple(map(round,nj["elbow_l"]))
n_wrist=tuple(map(round,nj["wrist_l"]))
n_tip=tuple(map(round,neutral_pose["stickTip"]))
d.line([n_shoulder,n_elbow,n_wrist],fill=255,width=165,joint="curve")
for p,r in [(n_shoulder,88),(n_elbow,92),(n_wrist,86)]:
    d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
d.line([n_wrist,n_tip],fill=255,width=46)
d.ellipse([n_tip[0]-30,n_tip[1]-30,n_tip[0]+30,n_tip[1]+30],fill=255)

# Restrict lower mask to upper-body/action area so legs/stool cannot be imported.
ma=np.asarray(mask).copy()
ma[570:,:]=0
# Absolute static guards: never import source head/right side/pelvis-seat pixels.
ma[0:325,500:930]=0
ma[560:810,560:980]=0
# Human visual QA v4 diagnosis: both neutral residue and source artifact
# contributed to the detached white crescent below the rebound stick.
# Keep the old-hand corridor replaceable, then explicitly clear only pixels
# sufficiently below the grip-to-tip stick axis inside a narrow local ROI.
ma[435:545,455:570]=255
mask=Image.fromarray(ma.astype(np.uint8),"L")

candidate=neutral.copy()
candidate.paste(source,(0,0),mask)

# Artifact-clear mask: x 455..545 only, and >18 px below the rebound stick axis
# from tip(438,418) to wrist(593,496). This preserves the stick shaft and grip.
qa=np.asarray(candidate).copy()
allowed=np.asarray(mask)>0
for x in range(455,546):
    stick_y = 418 + (496-418) * ((x-438)/(593-438))
    y0=max(0,int(round(stick_y+18)))
    y1=min(H,545)
    if y0<y1:
        qa[y0:y1,x,:]=0
        allowed[y0:y1,x]=True
candidate=Image.fromarray(qa,"RGBA")
mask=Image.fromarray((allowed.astype(np.uint8)*255),"L")

# Human visual QA v8: source rebound contains a second non-authoritative
# upper-left hand/stick. Do NOT restore a broad rectangle/corridor from neutral:
# that produced the v7 plaid/jacket patch. Instead, restore only pixels inside
# the diagnosed unwanted-hand ROI that actually differ between source and
# approved neutral, with a very small dilation to remove line-edge residue.
roi=Image.new("L",(W,H),0)
rd=ImageDraw.Draw(roi)
rd.line([(600,300),(675,405)],fill=255,width=54)
rd.ellipse([625,355,720,450],fill=255)
rd.line([(675,405),(650,462)],fill=255,width=82)
roi_arr=np.asarray(roi)>0
source_diff=np.any(np.asarray(source)!=np.asarray(neutral),axis=2)
restore_arr=roi_arr & source_diff
restore_img=Image.fromarray((restore_arr.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(5))
candidate.paste(neutral,(0,0),restore_img)
allowed |= (np.asarray(restore_img)>0)
mask=Image.fromarray((allowed.astype(np.uint8)*255),"L")

candidate_path=OUTDIR/"sn_l_rebound_candidate_v8.png"
candidate.save(candidate_path)

# Exact raster diagnostics.
n=np.asarray(neutral); s=np.asarray(source); q=np.asarray(candidate); mm=np.asarray(mask)>0
diff_nq=np.any(n!=q,axis=2)
diff_sq=np.any(s!=q,axis=2)
outside_changed=int(np.count_nonzero(diff_nq & ~mm))
inside_changed=int(np.count_nonzero(diff_nq & mm))
changed=int(np.count_nonzero(diff_nq))
ys,xs=np.nonzero(diff_nq)
bbox=None if xs.size==0 else {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}
# Compare inactive lower body/seat directly to neutral.
inactive_lower_changed=int(np.count_nonzero(np.any(n[720:,:,:]!=q[720:,:,:],axis=2)))
# head/core guard boxes chosen from approved-neutral geometry/tool landmarks.
guards={
 "head":[500,0,430,325],
 "right_arm":[820,320,340,250],
 "pelvis_seat":[560,560,420,250],
 "legs_stool":[300,700,850,386]
}
guard_changed={}
for name,(x,y,w,h) in guards.items():
 guard_changed[name]=int(np.count_nonzero(np.any(n[y:y+h,x:x+w,:]!=q[y:y+h,x:x+w,:],axis=2)))

# Constraint semantics.
def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
rebound_sep=dist(c["stickTip"],c["contactPoint"])

# Composite debug: drum under candidate, preserving source canvas.
comp=Image.alpha_composite(drum,candidate)
comp.save(OUTDIR/"sn_l_rebound_candidate_v8_fixed_drum.png")

report={
 "schemaVersion":8,
 "issueId":"MOTION-001",
 "actionKey":"SN:L",
 "phase":"rebound",
 "candidate":str(candidate_path.relative_to(ROOT)),
 "method":"approved neutral base + source rebound pixels only inside semantic left-arm/stick corridor",
 "source":{"neutralSha256":hashlib.sha256(neutral_path.read_bytes()).hexdigest(),"reboundSha256":hashlib.sha256(source_path.read_bytes()).hexdigest(),"constraint":str(constraint_path.relative_to(ROOT))},
 "semanticMask":{"shoulder":shoulder,"elbow":elbow,"wrist":wrist,"stickTip":tip,"maskPixelCount":int(mm.sum()),"lowerCutoffY":570},
 "constraintChecks":{"reboundSeparationPx":round(rebound_sep,3),"minimumSeparationPx":c["tolerancesPx"]["reboundSeparation"],"reboundPass":rebound_sep>=c["tolerancesPx"]["reboundSeparation"],"stoolAnchor":c["stoolAnchor"],"hipAnchor":c["hipAnchor"]},
 "rasterChecks":{"changedPixelsVsNeutral":changed,"changedRatioVsNeutral":round(changed/(W*H),8),"changedBBoxVsNeutral":bbox,"outsideMaskChangedPixels":outside_changed,"inactiveLowerBodyChangedPixels":inactive_lower_changed,"guardChangedPixels":guard_changed,"sourcePixelsRejectedOutsideMask":int(np.count_nonzero(diff_sq & ~mm))},
 "hardPass":{"outsideMaskChangedPixels":outside_changed==0,"inactiveLowerBodyChangedPixels":inactive_lower_changed==0,"headGuardChangedPixels":guard_changed["head"]==0,"rightArmGuardChangedPixels":guard_changed["right_arm"]==0,"pelvisSeatGuardChangedPixels":guard_changed["pelvis_seat"]==0,"legsStoolGuardChangedPixels":guard_changed["legs_stool"]==0,"reboundSeparation":rebound_sep>=c["tolerancesPx"]["reboundSeparation"]},
}
report["pass"]=all(report["hardPass"].values())
(OUTDIR/"sn_l_rebound_candidate_v8_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")

# v9 cumulative repair: keep the v8 cleaned rebound left arm/stick, but use the
# formal hit as the static parent so inactive right arm/head/torso/stool/legs do
# not jump between hit and rebound. Only pixels that actually differ between
# hit and v8 inside the UNION of hit+rebound left-arm/stick semantic corridors
# are replaced, with a very small dilation for line-edge continuity.
hit_image_path=ROOT/"character-assets/layers/character/sn/hit_l.png"
hit_image=Image.open(hit_image_path).convert("RGBA")
assert hit_image.size==candidate.size

hj=hit["joints"]
h_shoulder=tuple(map(round,hj["shoulder_l"]))
h_elbow=tuple(map(round,hj["elbow_l"]))
h_wrist=tuple(map(round,hj["wrist_l"]))
h_tip=tuple(map(round,hit["stickTip"]))

pair_roi=Image.new("L",(W,H),0)
pd=ImageDraw.Draw(pair_roi)
for pts,width in [([h_elbow,h_wrist],118),([elbow,wrist],118)]:
    pd.line(pts,fill=255,width=width,joint="curve")
for p,radius in [(h_elbow,72),(h_wrist,82),(elbow,72),(wrist,82)]:
    pd.ellipse([p[0]-radius,p[1]-radius,p[0]+radius,p[1]+radius],fill=255)
for a,b,width in [(h_wrist,h_tip,50),(wrist,tip,50)]:
    pd.line([a,b],fill=255,width=width)
for p,radius in [(h_tip,34),(tip,34)]:
    pd.ellipse([p[0]-radius,p[1]-radius,p[0]+radius,p[1]+radius],fill=255)

pair_roi_arr=np.asarray(pair_roi)>0
# Hard-exclude static zones from the pair replacement ROI itself. The active
# SN left arm/stick is entirely below the head lock and above the pelvis lock;
# allowing those pixels only creates false hair/waist drift.
pair_roi_arr[0:325,500:930]=False
pair_roi_arr[560:810,560:980]=False
pair_roi_arr[:,800:]=False
hit_arr=np.asarray(hit_image)
v8_arr=np.asarray(candidate)
pair_diff=np.any(hit_arr!=v8_arr,axis=2)
pair_replace_arr=pair_roi_arr & pair_diff
pair_replace_dil=np.asarray(Image.fromarray((pair_replace_arr.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(5)))>0
# Re-apply static exclusions AFTER dilation so edge growth cannot leak into
# head/pelvis/right-side guards.
pair_replace_dil[0:325,500:930]=False
pair_replace_dil[560:810,560:980]=False
pair_replace_dil[:,800:]=False
pair_replace=Image.fromarray((pair_replace_dil.astype(np.uint8)*255),"L")

candidate_v10=hit_image.copy()
candidate_v10.paste(candidate,(0,0),pair_replace)
candidate_v10_path=OUTDIR/"sn_l_rebound_candidate_v10.png"
candidate_v10.save(candidate_v10_path)

v9=np.asarray(candidate_v10)
pair_mask=np.asarray(pair_replace)>0
diff_hit_v9=np.any(hit_arr!=v9,axis=2)
outside_pair=int(np.count_nonzero(diff_hit_v9 & ~pair_mask))
ys9,xs9=np.nonzero(diff_hit_v9)
bbox9=None if xs9.size==0 else {"x":int(xs9.min()),"y":int(ys9.min()),"width":int(xs9.max()-xs9.min()+1),"height":int(ys9.max()-ys9.min()+1)}

pair_guards={
 "head":[500,0,430,325],
 "right_arm":[820,320,340,250],
 "pelvis_seat":[560,560,420,250],
 "legs_stool":[300,700,850,386]
}
pair_guard_changed={}
for name,(x,y,w,h) in pair_guards.items():
    pair_guard_changed[name]=int(np.count_nonzero(np.any(hit_arr[y:y+h,x:x+w,:]!=v9[y:y+h,x:x+w,:],axis=2)))

# Ensure the inactive right side is exactly inherited from hit.
inactive_right_exact=pair_guard_changed["right_arm"]==0
head_exact=pair_guard_changed["head"]==0
pelvis_exact=pair_guard_changed["pelvis_seat"]==0
legs_exact=pair_guard_changed["legs_stool"]==0

comp10=Image.alpha_composite(drum,candidate_v10)
comp10.save(OUTDIR/"sn_l_rebound_candidate_v10_fixed_drum.png")

report10={
 "schemaVersion":10,
 "issueId":"MOTION-001",
 "actionKey":"SN:L",
 "phase":"rebound",
 "candidate":str(candidate_v10_path.relative_to(ROOT)),
 "method":"formal hit static parent + v8 rebound elbow-forearm-hand-stick delta only",
 "parent":{
   "staticBase":str(hit_image_path.relative_to(ROOT)),
   "staticBaseSha256":hashlib.sha256(hit_image_path.read_bytes()).hexdigest(),
   "activeMotionParent":str(candidate_path.relative_to(ROOT)),
   "activeMotionParentSha256":hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
   "rollbackCandidate":"sn_l_rebound_candidate_v8.png"
 },
 "changedRoi":{"maskPixelCount":int(pair_mask.sum()),"changedPixelsVsHit":int(diff_hit_v9.sum()),"changedBBoxVsHit":bbox9},
 "pairStaticGuards":{"outsidePairMaskChangedPixels":outside_pair,"guardChangedPixelsVsHit":pair_guard_changed},
 "constraintChecks":{"reboundSeparationPx":round(rebound_sep,3),"minimumSeparationPx":c["tolerancesPx"]["reboundSeparation"],"reboundPass":rebound_sep>=c["tolerancesPx"]["reboundSeparation"]},
 "hardPass":{
   "outsidePairMaskChangedPixels":outside_pair==0,
   "inactiveRightArmExactToHit":inactive_right_exact,
   "headExactToHit":head_exact,
   "pelvisSeatExactToHit":pelvis_exact,
   "legsStoolExactToHit":legs_exact,
   "reboundSeparation":rebound_sep>=c["tolerancesPx"]["reboundSeparation"],
   "changedVisible":int(diff_hit_v9.sum())>=250
 }
}
report10["pass"]=all(report10["hardPass"].values())
(OUTDIR/"sn_l_rebound_candidate_v10_qa.json").write_text(json.dumps(report10,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v8":report,"v9":report10},ensure_ascii=False))
if not report10["pass"]: raise SystemExit(2)
