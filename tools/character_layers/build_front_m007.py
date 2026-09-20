#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m007"
OUT.mkdir(parents=True,exist_ok=True)
P={
 "neutral":ROOT/"character-assets/layers/character/base/neutral.png",
 "drum":ROOT/"character-assets/layers/drum/drum_base.png",
 "hit":ROOT/"character-assets/layers/character/hh/hit_r.png",
 "rebound":ROOT/"character-assets/layers/character/hh/rebound_r.png",
}
I={k:Image.open(v).convert("RGBA") for k,v in P.items()}
N=np.asarray(I["neutral"]);H,W=N.shape[:2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def diff(a,b):return np.any(np.asarray(a)!=np.asarray(b),axis=2)
def line_mask(points,width,circles=()):
 im=Image.new("L",(W,H),0);d=ImageDraw.Draw(im);d.line(points,fill=255,width=width,joint="curve")
 for x,y,r in circles:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.asarray(im)>0
def dil(m,n):
 if n%2==0:n+=1
 return np.asarray(Image.fromarray((m.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(n)))>0
def guard(m,r):
 x1,y1,x2,y2=r;return int(np.count_nonzero(m[y1:y2,x1:x2]))
def bbox(m):
 ys,xs=np.nonzero(m)
 return None if not xs.size else {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}

# Active HH corridor: only visible hand/forearm/stick from body edge to HH.
ACTIVE=line_mask([(680,405),(590,430),(470,440),(330,415),(190,390)],118,
 [(680,405,56),(590,430,60),(470,440,68),(330,415,52),(190,390,62)])
# Neutral right hand/stick residue corridor: paste donor including transparency
# so the old neutral right-hand pose disappears when the HH arm moves left.
RESIDUE=line_mask([(875,370),(920,468),(975,448),(1025,315)],118,
 [(875,370,62),(920,468,66),(975,448,70),(1025,315,42)])

HEAD=(500,0,930,305)
HAIR_CORE=(700,305,930,610)
PELVIS=(560,590,980,825)
STOOL=(760,690,850,1086)
TORSO_LOWER=(620,455,900,620)
LOWER=(0,620,W,H)

summary={"schemaVersion":5,"issueId":"MOTION-007","actionKey":"HH:R",
 "method":"neutral body + bounded HH active corridor + destructive neutral-right-arm residue clearing",
 "sources":{k:{"path":str(v.relative_to(ROOT)),"sha256":sha(v)} for k,v in P.items()},"phases":[]}
for phase in ("hit","rebound"):
 src=I[phase];S=np.asarray(src);sd=diff(src,I["neutral"])
 # Active corridor only where donor actually differs from neutral.
 m=(dil(sd,13)&ACTIVE) | RESIDUE
 # Preserve static anatomy absolutely.
 for rect in (HEAD,HAIR_CORE,TORSO_LOWER,PELVIS,STOOL):
  x1,y1,x2,y2=rect;m[y1:y2,x1:x2]=False
 m[620:,:]=False
 cand=I["neutral"].copy();cand.paste(src,(0,0),Image.fromarray((m*255).astype(np.uint8),"L"))
 # Structural cleanup: the source family retains the neutral right hand/stick
 # even after the active right arm crosses to HH. Remove that exact ghost and
 # reconstruct only the narrow hair edge it had occluded.
 erase=line_mask([(968,470),(1012,410),(1060,285)],92,[(982,438,78),(1040,310,46)])
 erase[:, :925]=False
 arr=np.asarray(cand).copy();arr[erase,:]=0
 cand=Image.fromarray(arr,"RGBA")
 repair=erase.copy()
 dr=ImageDraw.Draw(cand,"RGBA")
 # Interpolate the pre/post-occlusion outer hair silhouette. Fill only holes
 # created by the ghost removal; existing hair/body pixels stay untouched.
 edge=[]
 for yy in range(350,536):
     t=(yy-350)/(535-350)
     xb=int(round(930+t*42))
     edge.append((xb,yy))
     for xx in range(900,xb+1):
         if cand.getpixel((xx,yy))[3] < 32:
             cand.putpixel((xx,yy),(252,252,252,255))
             repair[yy,xx]=True
 # Rough-line contour, intentionally fine/repeated rather than one digital stroke.
 for dx in (-2,0,2):
     pts=[(x+dx,y) for x,y in edge]
     dr.line(pts,fill=(20,20,20,210),width=2)
     for x,y in pts:
         if 0<=x<W and 0<=y<H: repair[y,x]=True
 import math
 for off in (14,27,39):
     pts=[]
     for yy in range(365,526):
         t=(yy-350)/(535-350); xb=930+t*42
         xx=int(round(xb-off-3*math.sin((yy-350)/30)))
         pts.append((xx,yy))
         if 0<=xx<W and 0<=yy<H: repair[yy,xx]=True
     dr.line(pts,fill=(35,35,35,165),width=2)
 m |= repair
 C=np.asarray(cand);ch=np.any(C!=N,axis=2)
 exact=np.all(C==S,axis=2)
 # Donor fidelity applies only to active HH pixels. The explicit erase corridor
 # intentionally differs from the flawed formal donor and must not fail QA.
 active_rel=(m & sd & ~repair)
 pres=np.count_nonzero(active_rel&exact)/max(1,np.count_nonzero(active_rel))
 checks={
  "outsideMaskZero":bool(int(np.count_nonzero(ch&~m))==0),
  "headLocked":bool(guard(ch,HEAD)==0),
  "hairCoreLocked":bool(guard(ch,HAIR_CORE)==0),
  "torsoLowerLocked":bool(guard(ch,TORSO_LOWER)==0),
  "pelvisLocked":bool(guard(ch,PELVIS)==0),
  "stoolLocked":bool(guard(ch,STOOL)==0),
  "lowerBodyLocked":bool(int(np.count_nonzero(ch[620:,:]))==0),
  "donorExact":bool(pres>=0.995),
  "motionVisible":bool(int(np.count_nonzero(ch&ACTIVE))>=500),
 }
 cp=OUT/f"hh_{phase}_candidate_v5.png";cand.save(cp)
 Image.alpha_composite(I["drum"],cand).save(OUT/f"hh_{phase}_candidate_v5_fixed_drum.png")
 rec={"phase":phase,"candidate":str(cp.relative_to(ROOT)),"candidateSha256":sha(cp),
  "maskPixels":int(m.sum()),"changedPixelsVsNeutral":int(ch.sum()),"changedBBoxVsNeutral":bbox(ch),
  "donorPreserveRatio":round(float(pres),4),"checks":checks,"machinePass":all(checks.values())}
 (OUT/f"hh_{phase}_candidate_v5_qa.json").write_text(json.dumps(rec,indent=2)+"\n")
 summary["phases"].append(rec)
frames=[I["neutral"],Image.open(OUT/"hh_hit_candidate_v5.png").convert("RGBA"),Image.open(OUT/"hh_rebound_candidate_v5.png").convert("RGBA"),I["neutral"]]
strip=Image.new("RGB",(1920,360),"white")
for i,f in enumerate(frames):
 c=Image.alpha_composite(I["drum"],f).convert("RGB");c.thumbnail((480,360));strip.paste(c,(i*480,0))
strip.save(OUT/"hh_v5_transition.jpg",quality=95)
summary["pairMachinePass"]=all(x["machinePass"] for x in summary["phases"])
(OUT/"M007_V5_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({"pairMachinePass":summary["pairMachinePass"],"phases":[(x["phase"],x["candidateSha256"]) for x in summary["phases"]]}))
if not summary["pairMachinePass"]:raise SystemExit(2)
