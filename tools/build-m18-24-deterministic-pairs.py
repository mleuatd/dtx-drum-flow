from __future__ import annotations
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"character-assets/layers/character/combo"
QA=ROOT/"character-assets/generated-qa/m18-24"
pairs={
"bd_rd_rf_r":("rd/hit_r_refresh.png","rd/rebound_r_refresh.png","BD",["a3cba5e7199fa0c1e41fcba9d0918cf9d5d70b37d0bb1ff1e91503d2a0d42415","c370ad69756bda1b7fb9df066195c19bdce0b16f0a0459f3676e35851cba63b4"]),
"rd_sn_r_l":("rd/hit_r_refresh.png","rd/rebound_r_refresh.png","SN",["a3cba5e7199fa0c1e41fcba9d0918cf9d5d70b37d0bb1ff1e91503d2a0d42415","c370ad69756bda1b7fb9df066195c19bdce0b16f0a0459f3676e35851cba63b4"]),
"bd_hh_rf_r":("hh/hit_r.png","hh/rebound_r.png","BD",["c9d86e9970e8da2d9dac2ef486b7fe7b5d03e540c015b0158c70340b3c01eefd","f4060fbf0ab37938267267a89ef4ceb6ca1dba9c24154bf22dafa192d94fabb6"]),
"hh_sn_r_l":("hh/hit_r.png","hh/rebound_r.png","SN",["c9d86e9970e8da2d9dac2ef486b7fe7b5d03e540c015b0158c70340b3c01eefd","f4060fbf0ab37938267267a89ef4ceb6ca1dba9c24154bf22dafa192d94fabb6"])
}
BASE=ROOT/"character-assets/layers/character"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cue(im,kind,phase):
 s=4;l=Image.new("RGBA",(im.width*s,im.height*s),(0,0,0,0));d=ImageDraw.Draw(l)
 if kind=="BD": seg=[((470,820),(452,805)),((482,815),(474,792)),((495,817),(494,791))] if phase=="hit" else [((482,820),(470,810))]
 else: seg=[((405,535),(420,520)),((415,540),(430,525))] if phase=="hit" else [((405,525),(420,510))]
 for a,b in seg:d.line([(a[0]*s,a[1]*s),(b[0]*s,b[1]*s)],fill=(18,18,18,255),width=4*s)
 return Image.alpha_composite(im,l.resize(im.size,Image.Resampling.LANCZOS))
OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True);res={}
for key,(hp,rp,kind,shas) in pairs.items():
 res[key]={}
 for phase,rel,expect in [("hit",hp,shas[0]),("rebound",rp,shas[1])]:
  src=BASE/rel
  if sha(src)!=expect: raise SystemExit(f"{key} {phase} source SHA mismatch")
  base=Image.open(src).convert("RGBA"); cand=cue(base.copy(),kind,phase); out=OUT/f"{key}_{phase}_refresh.png";cand.save(out)
  diff=ImageChops.difference(base,cand);changed=sum(1 for p in diff.getdata() if p!=(0,0,0,0))
  res[key][phase]={"source":str(src.relative_to(ROOT)),"sourceSha256":expect,"path":str(out.relative_to(ROOT)),"sha256":sha(out),"changedPixelRatio":changed/(base.width*base.height),"diffBBox":diff.getbbox()}
(QA/"build-result.json").write_text(json.dumps(res,indent=2)+"\n")
print(json.dumps(res,indent=2))
