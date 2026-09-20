#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m004-v3"
OUT.mkdir(parents=True,exist_ok=True)

P={
 "neutral":ROOT/"character-assets/layers/character/base/neutral.png",
 "drum":ROOT/"character-assets/layers/drum/drum_base.png",
 "rc_hit":ROOT/"character-assets/layers/character/rc/hit_r_refresh.png",
 "rc_rebound":ROOT/"character-assets/layers/character/rc/rebound_r_refresh.png",
 "sn_hit":ROOT/"character-assets/layers/character/sn/hit_l.png",
 "sn_rebound":ROOT/"character-assets/layers/character/sn/rebound_l.png",
}
I={k:Image.open(v).convert("RGBA") for k,v in P.items()}
N=np.asarray(I["neutral"]); H,W=N.shape[:2]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def diff(a,b): return np.any(np.asarray(a)!=np.asarray(b),axis=2)
def dil(m,n):
    if n%2==0:n+=1
    return np.asarray(Image.fromarray((m.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(n)))>0
def line_mask(points,width,circles=()):
    im=Image.new("L",(W,H),0); d=ImageDraw.Draw(im)
    d.line(points,fill=255,width=width,joint="curve")
    for x,y,r in circles:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
    return np.asarray(im)>0
def bbox(m):
    ys,xs=np.nonzero(m)
    return None if not xs.size else {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}
def guard(m,r):
    x1,y1,x2,y2=r; return int(np.count_nonzero(m[y1:y2,x1:x2]))

# Same proven destructive RC rule used by VERIFIED MOTION-002.
RC_SEM=np.zeros((H,W),bool); RC_SEM[:590,700:]=True

# Left-arm corridors are geometry-driven, not rectangular body crops.
# Include both neutral pose and target pose so the old neutral hand/stick is
# destructively removed instead of remaining as a duplicate.
neutral_left=line_mask([(635,342),(585,470),(505,490),(432,384)],112,
 [(635,342,58),(585,470,62),(505,490,66),(432,384,34)])
neutral_left_residue=line_mask([(505,490),(432,384)],74,[(505,490,70),(432,384,38)])
neutral_right_residue=line_mask([(975,448),(1025,315),(1065,255)],104,
 [(975,448,78),(1025,315,54),(1065,255,40)])
sn_hit_geom=line_mask([(635,342),(595,473),(516,449),(420,535)],110,
 [(635,342,56),(595,473,62),(516,449,64),(420,535,38)])
sn_reb_geom=line_mask([(635,342),(657,474),(593,496),(438,418)],110,
 [(635,342,56),(657,474,62),(593,496,64),(438,418,38)])

# Absolute locks. These deliberately keep central hair/pelvis/stool on neutral.
HAIR_CORE=(700,315,900,610)
PELVIS=(560,590,980,825)
STOOL=(760,700,850,1086)
LOWER=(0,620,W,H)

summary={"schemaVersion":5,"issueId":"MOTION-004","actionKey":"RC+SN:R/L",
 "method":"neutral common body + VERIFIED RC donor + VERIFIED formal SN:L donor; no combo-source body pixels",
 "sources":{k:{"path":str(v.relative_to(ROOT)),"sha256":sha(v)} for k,v in P.items()},"phases":[]}

for phase in ("hit","rebound"):
    rc=I["rc_"+phase]
    sn=I["sn_"+phase]
    rd=diff(rc,I["neutral"]); sd=diff(sn,I["neutral"])

    rc_mask=(dil(rd,31)&RC_SEM) | neutral_right_residue

    geom=sn_hit_geom if phase=="hit" else sn_reb_geom
    # Only source pixels in/near arm motion plus the neutral pose corridor.
    # Because rebound v8 is neutral-based, broad neutral-residue clearing is safe.
    sn_mask=(dil(sd,21)&geom) | neutral_left
    # keep SN entirely on left side and upper body
    sn_mask[:,760:]=False
    sn_mask[620:,:]=False

    # Central hair must never be transplanted from either active donor.
    for m in (rc_mask,sn_mask):
        x1,y1,x2,y2=HAIR_CORE; m[y1:y2,x1:x2]=False
        x1,y1,x2,y2=PELVIS; m[y1:y2,x1:x2]=False
        x1,y1,x2,y2=STOOL; m[y1:y2,x1:x2]=False

    overlap=rc_mask&sn_mask
    # Keep left SN ownership in overlap near center; RC remains right side.
    rc_mask &= ~overlap

    cand=I["neutral"].copy()
    cand.paste(sn,(0,0),Image.fromarray((sn_mask*255).astype(np.uint8),"L"))
    cand.paste(rc,(0,0),Image.fromarray((rc_mask*255).astype(np.uint8),"L"))
    C=np.asarray(cand); changed=np.any(C!=N,axis=2); union=sn_mask|rc_mask

    R=np.asarray(rc); S=np.asarray(sn)
    exact_r=np.all(C==R,axis=2); exact_s=np.all(C==S,axis=2)
    rr=rc_mask&rd; ss=sn_mask&sd
    rpres=np.count_nonzero(rr&exact_r)/max(1,np.count_nonzero(rr))
    spres=np.count_nonzero(ss&exact_s)/max(1,np.count_nonzero(ss))

    checks={
      "outsideMaskZero":bool(int(np.count_nonzero(changed&~union))==0),
      "hairCoreLocked":bool(guard(changed,HAIR_CORE)==0),
      "pelvisLocked":bool(guard(changed,PELVIS)==0),
      "stoolLocked":bool(guard(changed,STOOL)==0),
      "lowerBodyLocked":bool(int(np.count_nonzero(changed[620:,:]))==0),
      "rcDonorExact":bool(rpres>=0.995),
      "snDonorExact":bool(spres>=0.985),
      "bothArmsVisible":bool(int(np.count_nonzero(rc_mask&changed))>500 and int(np.count_nonzero(sn_mask&changed))>500),
    }
    cp=OUT/f"rc_sn_{phase}_candidate_v5.png"; cand.save(cp)
    Image.alpha_composite(I["drum"],cand).save(OUT/f"rc_sn_{phase}_candidate_v5_fixed_drum.png")
    rec={"phase":phase,"candidate":str(cp.relative_to(ROOT)),"candidateSha256":sha(cp),
      "rcMaskPixels":int(rc_mask.sum()),"snMaskPixels":int(sn_mask.sum()),"overlapPixels":int(overlap.sum()),
      "changedPixelsVsNeutral":int(changed.sum()),"changedBBoxVsNeutral":bbox(changed),
      "rcDonorPreserveRatio":round(float(rpres),4),"snDonorPreserveRatio":round(float(spres),4),
      "checks":checks,"machinePass":all(checks.values())}
    (OUT/f"rc_sn_{phase}_candidate_v5_qa.json").write_text(json.dumps(rec,indent=2)+"\n")
    summary["phases"].append(rec)

# Visual transition evidence.
frames=[I["neutral"],Image.open(OUT/"rc_sn_hit_candidate_v5.png").convert("RGBA"),Image.open(OUT/"rc_sn_rebound_candidate_v5.png").convert("RGBA"),I["neutral"]]
strip=Image.new("RGB",(1920,360),"white")
for i,f in enumerate(frames):
    comp=Image.alpha_composite(I["drum"],f).convert("RGB"); comp.thumbnail((480,360))
    strip.paste(comp,(i*480,0))
strip.save(OUT/"rc_sn_v5_transition.jpg",quality=95)
summary["pairMachinePass"]=all(x["machinePass"] for x in summary["phases"])
(OUT/"M004_V5_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")

# v6: source-bound local repair from the exact v5 parent.
# Full-resolution visual QA found one inactive SN-donor hand/forearm/stick
# remaining above the intended SN arm. Restore only this measured ROI from
# the neutral/common-body authority. Nothing outside this rectangle may move.
V6_REPAIR_ROI=(560,270,720,445)
v6={"schemaVersion":6,"issueId":"MOTION-004","actionKey":"RC+SN:R/L",
 "parentVersion":"v5","repairType":"source_bound_local_reconstruction",
 "repairRoiPx":{"x":560,"y":270,"width":160,"height":175},
 "repairReason":"remove inactive SN-donor upper hand/forearm/stick residue found by full-resolution visual QA",
 "sources":summary["sources"],"phases":[]}

for phase in ("hit","rebound"):
    v5p=OUT/f"rc_sn_{phase}_candidate_v5.png"
    parent=Image.open(v5p).convert("RGBA")
    cand=parent.copy()
    cand.paste(I["neutral"].crop(V6_REPAIR_ROI),V6_REPAIR_ROI)
    cp=OUT/f"rc_sn_{phase}_candidate_v6.png"
    cand.save(cp)
    Image.alpha_composite(I["drum"],cand).save(OUT/f"rc_sn_{phase}_candidate_v6_fixed_drum.png")

    A=np.asarray(parent); C=np.asarray(cand)
    changed=np.any(A!=C,axis=2)
    roi=np.zeros((H,W),bool)
    x1,y1,x2,y2=V6_REPAIR_ROI; roi[y1:y2,x1:x2]=True
    checks={
      "outsideV5RepairRoiZero":bool(int(np.count_nonzero(changed&~roi))==0),
      "pelvisLocked":bool(guard(changed,PELVIS)==0),
      "stoolLocked":bool(guard(changed,STOOL)==0),
      "lowerBodyLocked":bool(int(np.count_nonzero(changed[620:,:]))==0),
      "canvasLocked":bool(cand.size==parent.size==(W,H)),
    }
    rec={"phase":phase,"candidate":str(cp.relative_to(ROOT)),"candidateSha256":sha(cp),
      "parentCandidateSha256":sha(v5p),"repairChangedPixels":int(changed.sum()),
      "repairChangedBBox":bbox(changed),"checks":checks,"machinePass":all(checks.values())}
    (OUT/f"rc_sn_{phase}_candidate_v6_qa.json").write_text(json.dumps(rec,indent=2)+"\n")
    v6["phases"].append(rec)

frames=[I["neutral"],Image.open(OUT/"rc_sn_hit_candidate_v6.png").convert("RGBA"),Image.open(OUT/"rc_sn_rebound_candidate_v6.png").convert("RGBA"),I["neutral"]]
strip=Image.new("RGB",(1920,360),"white")
for i,f in enumerate(frames):
    comp=Image.alpha_composite(I["drum"],f).convert("RGB"); comp.thumbnail((480,360))
    strip.paste(comp,(i*480,0))
strip.save(OUT/"rc_sn_v6_transition.jpg",quality=95)
v6["pairMachinePass"]=all(x["machinePass"] for x in v6["phases"])
(OUT/"M004_V6_SUMMARY.json").write_text(json.dumps(v6,indent=2)+"\n")

print(json.dumps({
 "v5PairMachinePass":summary["pairMachinePass"],
 "v6PairMachinePass":v6["pairMachinePass"],
 "v6Phases":[(x["phase"],x["candidateSha256"]) for x in v6["phases"]]
}))
if not summary["pairMachinePass"]: raise SystemExit(2)
if not v6["pairMachinePass"]: raise SystemExit(3)
