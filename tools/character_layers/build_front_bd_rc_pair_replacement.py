#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

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
N=np.array(imgs["neutral"]); H,W=N.shape[:2]

def sha(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def diff_mask(a,b): return np.any(np.array(a)!=np.array(b),axis=2)
def dilate(mask,size):
    if size%2==0:size+=1
    return np.array(Image.fromarray((mask.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(size)))>0
def bbox(mask):
    ys,xs=np.nonzero(mask)
    if len(xs)==0:return None
    return {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}
def guard_count(changed,rect):
    x1,y1,x2,y2=rect
    return int(np.count_nonzero(changed[y1:y2,x1:x2]))
def polyline_mask(points,width,circles=()):
    im=Image.new("L",(W,H),0); d=ImageDraw.Draw(im)
    d.line(points,fill=255,width=width,joint="curve")
    for (x,y,r) in circles:
        d.ellipse((x-r,y-r,x+r,y+r),fill=255)
    return np.array(im)>0

HEAD=(500,0,930,315)
LEFT_LOCK=(0,250,520,900)
STOOL_CORE=(770,800,845,1086)
RC_SEM=np.zeros((H,W),bool); RC_SEM[:590,700:]=True
# RF corridor follows the verified BD donor's active leg only; skirt/pelvis are not blanket-transplanted.
RF_CORRIDOR=polyline_mask([(875,655),(682,748),(650,902)],170,[(875,655,75),(682,748,80),(650,902,100)])

summary={
 "schemaVersion":2,"issueId":"MOTION-002","actionKey":"BD+RC:RF/R","batch":"HOLD-REPAIR-FRONT-06",
 "method":"v2: keep v1 RC destructive replacement; narrow BD/RF transplant to articulated RF corridor; lock skirt/pelvis/stool core",
 "parentEvidence":{
   "hit":{"candidateSha256":"beef2e3762f945eb6b222e1bbb59c55f8747b204ec30be4fac93b9a4c3aaac7d"},
   "rebound":{"candidateSha256":"36b83c287a3e9e5e3e000671418f9aea28de97f8fee6efc1f3226b7872a9c2ef"}
 },
 "sources":{k:{"path":v,"sha256":sha(v)} for k,v in paths.items()},"phases":[]
}

for phase in ("hit","rebound"):
    bd=imgs["bd_"+phase]; rc=imgs["rc_"+phase]
    B=np.array(bd); R=np.array(rc)
    bd_diff=diff_mask(bd,imgs["neutral"]); rc_diff=diff_mask(rc,imgs["neutral"])

    # One coherent right arm: destructive donor replacement, not additive overlay.
    rc_mask=dilate(rc_diff,31) & RC_SEM

    # Preserve only verified RF-leg motion from the BD donor.
    bd_mask=dilate(bd_diff,21) & RF_CORRIDOR
    # Never rewrite fixed stool core; active leg remains outside this structural lock.
    x1,y1,x2,y2=STOOL_CORE
    bd_mask[y1:y2,x1:x2]=False

    overlap=rc_mask & bd_mask
    rc_mask &= ~overlap

    cand=imgs["neutral"].copy()
    cand.paste(rc,(0,0),Image.fromarray((rc_mask*255).astype(np.uint8),"L"))
    cand.paste(bd,(0,0),Image.fromarray((bd_mask*255).astype(np.uint8),"L"))
    C=np.array(cand)
    changed=np.any(C!=N,axis=2); union=rc_mask|bd_mask

    exact_rc=np.all(C==R,axis=2); exact_bd=np.all(C==B,axis=2)
    rc_rel=rc_mask & rc_diff
    bd_rel=bd_mask & bd_diff
    rc_pres=np.count_nonzero(rc_rel & exact_rc)/max(1,np.count_nonzero(rc_rel))
    bd_pres=np.count_nonzero(bd_rel & exact_bd)/max(1,np.count_nonzero(bd_rel))

    # Motion visibility in lower RF region, avoiding the stool core.
    rf_visible=np.count_nonzero(changed & RF_CORRIDOR)
    checks={
      "maskDisjoint":int(np.count_nonzero(overlap))==0,
      "outsideMaskZero":int(np.count_nonzero(changed & ~union))==0,
      "headLocked":guard_count(changed,HEAD)==0,
      "leftSideLocked":guard_count(changed,LEFT_LOCK)==0,
      "stoolCoreLocked":guard_count(changed,STOOL_CORE)==0,
      "rcDonorExactInActiveMask":rc_pres>=0.995,
      "bdDonorExactInActiveMask":bd_pres>=0.995,
      "rfMotionVisible":rf_visible>=1000,
      "candidateDiffVisible":int(np.count_nonzero(changed))>500,
    }
    stem=f"bd_rc_{phase}_candidate_v2"
    cp=OUT/(stem+".png"); cand.save(cp)
    Image.alpha_composite(imgs["drum"],cand).save(OUT/(stem+"_fixed_drum.png"))
    rec={
      "phase":phase,"parentCandidate":"v1","candidate":str(cp.relative_to(ROOT)),
      "candidateSha256":hashlib.sha256(cp.read_bytes()).hexdigest(),
      "changedRois":["RC right-arm destructive replacement","narrow BD/RF articulated leg corridor"],
      "improvementIntent":["remove v1 skirt/pelvis rewrite","preserve stool core","retain single RC arm/hand/stick"],
      "rcMaskPixels":int(np.count_nonzero(rc_mask)),"bdMaskPixels":int(np.count_nonzero(bd_mask)),
      "maskOverlapPixels":int(np.count_nonzero(overlap)),
      "changedPixelsVsNeutral":int(np.count_nonzero(changed)),"changedBBoxVsNeutral":bbox(changed),
      "rcDonorPreserveRatio":round(float(rc_pres),4),"bdDonorPreserveRatio":round(float(bd_pres),4),
      "rfMotionVisiblePixels":int(rf_visible),"checks":checks,"machinePass":all(checks.values())
    }
    (OUT/(stem+"_qa.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    summary["phases"].append(rec)

# transition strip: neutral -> hit -> rebound
strip=Image.new("RGBA",(W*3,H),(255,255,255,0))
strip.paste(imgs["neutral"],(0,0),imgs["neutral"])
for i,phase in enumerate(("hit","rebound"),1):
    im=Image.open(OUT/f"bd_rc_{phase}_candidate_v2.png").convert("RGBA")
    strip.paste(im,(W*i,0),im)
strip.save(OUT/"bd_rc_v2_transition_strip.png")
summary["pairMachinePass"]=all(x["machinePass"] for x in summary["phases"])
summary["nextGate"]="full-resolution human anatomy + arm/hand/stick + linework + fixed-drum + transition QA"
(OUT/"FRONT06_CANDIDATE_SUMMARY_V2.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"pairMachinePass":summary["pairMachinePass"],"out":str(OUT.relative_to(ROOT))}))
