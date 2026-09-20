#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front06"
OUT.mkdir(parents=True, exist_ok=True)

paths={
 "neutral":"character-assets/layers/character/base/neutral.png",
 "bd_hit":"character-assets/layers/character/bd/hit_rf.png",
 "bd_rebound":"character-assets/layers/character/bd/rebound_rf.png",
 "rc_hit":"character-assets/layers/character/rc/hit_r_refresh.png",
 "rc_rebound":"character-assets/layers/character/rc/rebound_r_refresh.png",
 "drum":"character-assets/layers/drum/drum_base.png",
}
imgs={k:Image.open(ROOT/v).convert("RGBA") for k,v in paths.items()}
N=np.array(imgs["neutral"])
H,W=N.shape[:2]

def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def diff_mask(a,b):
    return np.any(np.array(a)!=np.array(b),axis=2)

def dilate(mask, size):
    if size%2==0: size+=1
    return np.array(Image.fromarray((mask.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(size)))>0

def bbox(mask):
    ys,xs=np.nonzero(mask)
    if len(xs)==0: return None
    return {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}

def circle(cx,cy,r):
    yy,xx=np.ogrid[:H,:W]
    return (xx-cx)**2+(yy-cy)**2<=r*r

HEAD=(500,0,930,315)
TORSO_LOCK=(500,315,720,585)
LEFT_LOCK=(0,250,520,900)
STOOL=(760,690,850,1086)

summary={"schemaVersion":1,"issueId":"MOTION-002","actionKey":"BD+RC:RF/R","batch":"HOLD-REPAIR-FRONT-06",
         "method":"neutral base + destructive RC donor replacement + independent BD/RF donor replacement",
         "sources":{k:{"path":v,"sha256":sha(v)} for k,v in paths.items()},"phases":[]}

for phase in ("hit","rebound"):
    bd=imgs["bd_"+phase]
    rc=imgs["rc_"+phase]
    bd_diff=diff_mask(bd,imgs["neutral"])
    rc_diff=diff_mask(rc,imgs["neutral"])

    # Destructive replacement masks: include both donor-added and neutral-residue pixels,
    # then constrain by independent semantic half-planes so arm and foot cannot overlap.
    rc_mask=dilate(rc_diff,31)
    yy,xx=np.ogrid[:H,:W]
    rc_sem=(xx>=700)&(yy<590)
    rc_mask &= rc_sem

    bd_mask=dilate(bd_diff,31)
    bd_sem=(xx>=520)&(xx<=1020)&(yy>=590)
    bd_mask &= bd_sem

    overlap=rc_mask & bd_mask
    if np.any(overlap):
        raise SystemExit("semantic masks overlap")

    cand=imgs["neutral"].copy()
    cand.paste(rc,(0,0),Image.fromarray((rc_mask*255).astype(np.uint8),"L"))
    cand.paste(bd,(0,0),Image.fromarray((bd_mask*255).astype(np.uint8),"L"))
    C=np.array(cand)
    changed=np.any(C!=N,axis=2)
    union=rc_mask|bd_mask

    # Contact preservation against donor in authoritative neighborhoods.
    rc_region=circle(1215,145,85 if phase=="hit" else 120)
    bd_region=circle(735,650,85 if phase=="hit" else 120)
    exact_rc=np.all(C==np.array(rc),axis=2)
    exact_bd=np.all(C==np.array(bd),axis=2)
    rc_rel=rc_region & rc_diff
    bd_rel=bd_region & bd_diff
    rc_pres=float(np.count_nonzero(rc_rel & exact_rc))/max(1,int(np.count_nonzero(rc_rel)))
    bd_pres=float(np.count_nonzero(bd_rel & exact_bd))/max(1,int(np.count_nonzero(bd_rel)))

    def guard(rect):
        x1,y1,x2,y2=rect
        return int(np.count_nonzero(changed[y1:y2,x1:x2]))

    checks={
      "maskDisjoint": int(np.count_nonzero(overlap))==0,
      "outsideMaskZero": int(np.count_nonzero(changed & ~union))==0,
      "headLocked": guard(HEAD)==0,
      "leftSideLocked": guard(LEFT_LOCK)==0,
      "stoolLocked": guard(STOOL)==0,
      "rcContactPreservation": rc_pres>=0.95,
      "bdContactPreservation": bd_pres>=0.95,
      "candidateDiffVisible": int(np.count_nonzero(changed))>500,
    }
    stem=f"bd_rc_{phase}_candidate_v1"
    cp=OUT/(stem+".png")
    cand.save(cp)
    comp=Image.alpha_composite(imgs["drum"],cand)
    comp.save(OUT/(stem+"_fixed_drum.png"))

    rec={
      "phase":phase,
      "candidate":str(cp.relative_to(ROOT)),
      "candidateSha256":hashlib.sha256(cp.read_bytes()).hexdigest(),
      "parent":"neutral + exact donor bytes",
      "changedRois":["RC right-arm replacement mask","BD/RF lower-leg-foot replacement mask"],
      "rcMaskPixels":int(np.count_nonzero(rc_mask)),
      "bdMaskPixels":int(np.count_nonzero(bd_mask)),
      "maskOverlapPixels":int(np.count_nonzero(overlap)),
      "changedPixelsVsNeutral":int(np.count_nonzero(changed)),
      "changedBBoxVsNeutral":bbox(changed),
      "rcContactPreserveRatio":round(rc_pres,4),
      "bdContactPreserveRatio":round(bd_pres,4),
      "checks":checks,
      "machinePass":all(checks.values()),
    }
    (OUT/(stem+"_qa.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    summary["phases"].append(rec)

# Pair transition strip for visual QA.
strip=Image.new("RGBA",(W*3,H),(255,255,255,0))
strip.paste(imgs["neutral"],(0,0),imgs["neutral"])
for i,phase in enumerate(("hit","rebound"),start=1):
    im=Image.open(OUT/f"bd_rc_{phase}_candidate_v1.png").convert("RGBA")
    strip.paste(im,(W*i,0),im)
strip.save(OUT/"bd_rc_v1_transition_strip.png")
summary["pairMachinePass"]=all(x["machinePass"] for x in summary["phases"])
summary["nextGate"]="full-resolution anatomy/linework/fixed-drum visual QA; do not promote formal from machine QA alone"
(OUT/"FRONT06_CANDIDATE_SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"pairMachinePass":summary["pairMachinePass"],"out":str(OUT.relative_to(ROOT))}))
