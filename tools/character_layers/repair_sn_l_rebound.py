#!/usr/bin/env python3
import json, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

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

# Human visual QA v6 diagnosis: source rebound itself contains a second,
# non-authoritative upper-left hand/stick. The authoritative rebound wrist is
# (593,496); the upper artifact sits around x640..700/y330..465. Restore only
# that artifact corridor from approved neutral, preserving the lower rebound
# hand/stick and all static regions.
restore=Image.new("L",(W,H),0)
rd=ImageDraw.Draw(restore)
rd.line([(600,300),(675,405)],fill=255,width=54)
rd.ellipse([625,355,720,450],fill=255)
rd.line([(675,405),(650,462)],fill=255,width=82)
candidate.paste(neutral,(0,0),restore)
allowed |= (np.asarray(restore)>0)
mask=Image.fromarray((allowed.astype(np.uint8)*255),"L")

candidate_path=OUTDIR/"sn_l_rebound_candidate_v7.png"
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
comp.save(OUTDIR/"sn_l_rebound_candidate_v7_fixed_drum.png")

report={
 "schemaVersion":7,
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
(OUTDIR/"sn_l_rebound_candidate_v7_qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report,ensure_ascii=False))
if not report["pass"]: raise SystemExit(2)
