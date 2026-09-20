#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m006"
OUT.mkdir(parents=True,exist_ok=True)
P={
 "neutral":ROOT/"character-assets/layers/character/base/neutral.png",
 "drum":ROOT/"character-assets/layers/drum/drum_base.png",
 "bd_hit":ROOT/"character-assets/layers/character/bd/hit_rf.png",
 "bd_rebound":ROOT/"character-assets/layers/character/bd/rebound_rf.png",
 "rd_hit":ROOT/"character-assets/layers/character/rd/hit_r_refresh.png",
 "rd_rebound":ROOT/"character-assets/layers/character/rd/rebound_r_refresh.png",
}
I={k:Image.open(v).convert("RGBA") for k,v in P.items()}
N=np.asarray(I["neutral"]); H,W=N.shape[:2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dmask(a,b): return np.any(np.asarray(a)!=np.asarray(b),axis=2)
def dil(m,n):
    if n%2==0:n+=1
    return np.asarray(Image.fromarray((m.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(n)))>0
def pathmask(points,width,circles=()):
    im=Image.new("L",(W,H),0); d=ImageDraw.Draw(im)
    d.line(points,fill=255,width=width,joint="curve")
    for x,y,r in circles:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
    return np.asarray(im)>0
def bbox(m):
    ys,xs=np.nonzero(m)
    return None if not xs.size else {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}
def guard(m,r):
    x1,y1,x2,y2=r; return int(np.count_nonzero(m[y1:y2,x1:x2]))

HEAD=(500,0,840,315)
TORSO=(590,315,825,590)
PELVIS=(560,590,980,700)
STOOL=(770,800,845,1086)

RD_GEOM=pathmask([(865,370),(925,330),(990,265),(1045,205)],150,
 [(865,370,70),(925,330,70),(990,265,60),(1045,205,55)])
RD_GEOM[:180,:]=False
RF=pathmask([(682,748),(650,902)],175,[(682,748,85),(650,902,105)])
RF[:700,:]=False

summary={"schemaVersion":1,"issueId":"MOTION-006","actionKey":"BD+RD:RF/R",
 "method":"neutral common body + VERIFIED M010 RD:R donor + VERIFIED M003 BD:RF donor",
 "sources":{k:{"path":str(v.relative_to(ROOT)),"sha256":sha(v)} for k,v in P.items()},"phases":[]}

for phase in ("hit","rebound"):
    bd=I["bd_"+phase]; rd=I["rd_"+phase]
    B=np.asarray(bd); R=np.asarray(rd)
    bd_diff=dmask(bd,I["neutral"]); rd_diff=dmask(rd,I["neutral"])
    rd_mask=dil(rd_diff,13)&RD_GEOM
    for rect in (HEAD,TORSO,PELVIS,STOOL):
        x1,y1,x2,y2=rect; rd_mask[y1:y2,x1:x2]=False
    rd_mask[620:,:]=False
    bd_mask=dil(bd_diff,21)&RF
    x1,y1,x2,y2=STOOL; bd_mask[y1:y2,x1:x2]=False
    overlap=rd_mask&bd_mask
    rd_mask &= ~overlap
    cand=I["neutral"].copy()
    cand.paste(rd,(0,0),Image.fromarray((rd_mask*255).astype(np.uint8),"L"))
    cand.paste(bd,(0,0),Image.fromarray((bd_mask*255).astype(np.uint8),"L"))
    C=np.asarray(cand); changed=np.any(C!=N,axis=2); union=rd_mask|bd_mask
    er=np.all(C==R,axis=2); eb=np.all(C==B,axis=2)
    rr=rd_mask&rd_diff; br=bd_mask&bd_diff
    rp=np.count_nonzero(rr&er)/max(1,np.count_nonzero(rr))
    bp=np.count_nonzero(br&eb)/max(1,np.count_nonzero(br))
    checks={
      "outsideMaskZero":bool(int(np.count_nonzero(changed&~union))==0),
      "headLocked":bool(guard(changed,HEAD)==0),
      "torsoLocked":bool(guard(changed,TORSO)==0),
      "pelvisLocked":bool(guard(changed,PELVIS)==0),
      "stoolLocked":bool(guard(changed,STOOL)==0),
      "rdDonorExact":bool(rp>=0.995),
      "bdDonorExact":bool(bp>=0.995),
      "rdMotionVisible":bool(int(np.count_nonzero(changed&RD_GEOM))>=300),
      "rfMotionVisible":bool(int(np.count_nonzero(changed&RF))>=1000),
    }
    cp=OUT/f"bd_rd_{phase}_candidate_v1.png"; cand.save(cp)
    Image.alpha_composite(I["drum"],cand).save(OUT/f"bd_rd_{phase}_candidate_v1_fixed_drum.png")
    rec={"phase":phase,"candidate":str(cp.relative_to(ROOT)),"candidateSha256":sha(cp),
      "rdMaskPixels":int(rd_mask.sum()),"bdMaskPixels":int(bd_mask.sum()),"overlapPixels":int(overlap.sum()),
      "changedPixelsVsNeutral":int(changed.sum()),"changedBBoxVsNeutral":bbox(changed),
      "rdPreserveRatio":round(float(rp),4),"bdPreserveRatio":round(float(bp),4),
      "checks":checks,"machinePass":all(checks.values())}
    (OUT/f"bd_rd_{phase}_candidate_v1_qa.json").write_text(json.dumps(rec,indent=2)+"\n")
    summary["phases"].append(rec)
frames=[I["neutral"],Image.open(OUT/"bd_rd_hit_candidate_v1.png").convert("RGBA"),Image.open(OUT/"bd_rd_rebound_candidate_v1.png").convert("RGBA"),I["neutral"]]
strip=Image.new("RGB",(1920,360),"white")
for i,f in enumerate(frames):
    c=Image.alpha_composite(I["drum"],f).convert("RGB"); c.thumbnail((480,360)); strip.paste(c,(i*480,0))
strip.save(OUT/"bd_rd_transition.jpg",quality=95)
summary["pairMachinePass"]=all(x["machinePass"] for x in summary["phases"])
(OUT/"M006_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({"pairMachinePass":summary["pairMachinePass"],"phases":[(x["phase"],x["candidateSha256"]) for x in summary["phases"]]}))
if not summary["pairMachinePass"]: raise SystemExit(2)
