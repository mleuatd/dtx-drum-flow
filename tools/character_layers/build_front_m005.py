#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m005"
OUT.mkdir(parents=True,exist_ok=True)
P={
 "neutral":ROOT/"character-assets/layers/character/base/neutral.png",
 "drum":ROOT/"character-assets/layers/drum/drum_base.png",
 "bd_hit":ROOT/"character-assets/layers/character/bd/hit_rf.png",
 "bd_rebound":ROOT/"character-assets/layers/character/bd/rebound_rf.png",
 "hh_hit":ROOT/"character-assets/layers/character/hh/hit_r.png",
 "hh_rebound":ROOT/"character-assets/layers/character/hh/rebound_r.png",
}
I={k:Image.open(v).convert("RGBA") for k,v in P.items()}
N=np.asarray(I["neutral"]); H,W=N.shape[:2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dmask(a,b):return np.any(np.asarray(a)!=np.asarray(b),axis=2)
def dil(m,n):
 if n%2==0:n+=1
 return np.asarray(Image.fromarray((m.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(n)))>0
def pathmask(points,width,circles=()):
 im=Image.new("L",(W,H),0);d=ImageDraw.Draw(im);d.line(points,fill=255,width=width,joint="curve")
 for x,y,r in circles:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.asarray(im)>0
def bbox(m):
 ys,xs=np.nonzero(m)
 return None if not xs.size else {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}
def guard(m,r):
 x1,y1,x2,y2=r;return int(np.count_nonzero(m[y1:y2,x1:x2]))

HEAD=(500,0,930,315)
PELVIS=(560,590,980,825)
STOOL=(770,800,845,1086)
LEFT_BODY=(0,600,600,1086)
# Right-hand HH strike/rebound corridor from right shoulder to HH playing surface.
HH_GEOM=pathmask([(875,370),(760,420),(600,430),(410,410),(190,390)],190,
 [(875,370,80),(760,420,85),(600,430,82),(410,410,72),(190,390,90)])
# Verified RF lower-leg corridor from MOTION-002 mechanism.
RF=pathmask([(682,748),(650,902)],175,[(682,748,85),(650,902,105)])
RF[:700,:]=False

summary={"schemaVersion":1,"issueId":"MOTION-005","actionKey":"BD+HH:RF/R",
 "method":"neutral common body + single-action HH destructive donor + VERIFIED BD RF donor",
 "sources":{k:{"path":str(v.relative_to(ROOT)),"sha256":sha(v)} for k,v in P.items()},"phases":[]}
for phase in ("hit","rebound"):
 bd=I["bd_"+phase]; hh=I["hh_"+phase]
 B=np.asarray(bd);QH=np.asarray(hh)
 bd_diff=dmask(bd,I["neutral"]);hh_diff=dmask(hh,I["neutral"])
 hh_mask=dil(hh_diff,25)&HH_GEOM
 # never import head/pelvis/stool from HH source
 x1,y1,x2,y2=HEAD;hh_mask[y1:y2,x1:x2]=False
 x1,y1,x2,y2=PELVIS;hh_mask[y1:y2,x1:x2]=False
 x1,y1,x2,y2=STOOL;hh_mask[y1:y2,x1:x2]=False
 hh_mask[620:,:]=False

 bd_mask=dil(bd_diff,21)&RF
 x1,y1,x2,y2=STOOL;bd_mask[y1:y2,x1:x2]=False

 overlap=hh_mask&bd_mask
 hh_mask&=~overlap
 cand=I["neutral"].copy()
 cand.paste(hh,(0,0),Image.fromarray((hh_mask*255).astype(np.uint8),"L"))
 cand.paste(bd,(0,0),Image.fromarray((bd_mask*255).astype(np.uint8),"L"))
 C=np.asarray(cand);changed=np.any(C!=N,axis=2);union=hh_mask|bd_mask
 eh=np.all(C==QH,axis=2);eb=np.all(C==B,axis=2)
 hr=hh_mask&hh_diff;br=bd_mask&bd_diff
 hp=np.count_nonzero(hr&eh)/max(1,np.count_nonzero(hr))
 bp=np.count_nonzero(br&eb)/max(1,np.count_nonzero(br))
 checks={
  "outsideMaskZero":bool(int(np.count_nonzero(changed&~union))==0),
  "headLocked":bool(guard(changed,HEAD)==0),
  "pelvisLocked":bool(guard(changed,PELVIS)==0),
  "stoolLocked":bool(guard(changed,STOOL)==0),
  "hhDonorExact":bool(hp>=0.995),
  "bdDonorExact":bool(bp>=0.995),
  "hhMotionVisible":bool(int(np.count_nonzero(changed&HH_GEOM))>=1000),
  "rfMotionVisible":bool(int(np.count_nonzero(changed&RF))>=1000),
 }
 cp=OUT/f"bd_hh_{phase}_candidate_v1.png";cand.save(cp)
 Image.alpha_composite(I["drum"],cand).save(OUT/f"bd_hh_{phase}_candidate_v1_fixed_drum.png")
 rec={"phase":phase,"candidate":str(cp.relative_to(ROOT)),"candidateSha256":sha(cp),
  "hhMaskPixels":int(hh_mask.sum()),"bdMaskPixels":int(bd_mask.sum()),"overlapPixels":int(overlap.sum()),
  "changedPixelsVsNeutral":int(changed.sum()),"changedBBoxVsNeutral":bbox(changed),
  "hhPreserveRatio":round(float(hp),4),"bdPreserveRatio":round(float(bp),4),
  "checks":checks,"machinePass":all(checks.values())}
 (OUT/f"bd_hh_{phase}_candidate_v1_qa.json").write_text(json.dumps(rec,indent=2)+"\n")
 summary["phases"].append(rec)
frames=[I["neutral"],Image.open(OUT/"bd_hh_hit_candidate_v1.png").convert("RGBA"),Image.open(OUT/"bd_hh_rebound_candidate_v1.png").convert("RGBA"),I["neutral"]]
strip=Image.new("RGB",(1920,360),"white")
for i,f in enumerate(frames):
 c=Image.alpha_composite(I["drum"],f).convert("RGB");c.thumbnail((480,360));strip.paste(c,(i*480,0))
strip.save(OUT/"bd_hh_transition.jpg",quality=95)
summary["pairMachinePass"]=all(x["machinePass"] for x in summary["phases"])
(OUT/"M005_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({"pairMachinePass":summary["pairMachinePass"],"phases":[(x["phase"],x["candidateSha256"]) for x in summary["phases"]]}))
if not summary["pairMachinePass"]:raise SystemExit(2)
