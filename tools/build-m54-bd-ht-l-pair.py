from __future__ import annotations
import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE_HIT=ROOT/"character-assets/layers/character/ht/hit_l_refresh.png"
BASE_REBOUND=ROOT/"character-assets/layers/character/ht/rebound_l_refresh.png"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
OUT=ROOT/"character-assets/review-candidates/m54"
QA=ROOT/"character-assets/generated-qa/m54/bd_ht_rf_l"
BASE_HIT_SHA="8a2fb872a4a650504306ea02d1b82ef3748c7c16186a807481e5ebf8fe272572"
BASE_REBOUND_SHA="5580cd68be8b7f277e7f3eac9759cb4a6837d8cf6ff79fb2df2b0da8d78519f0"

def sha256(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def add_kick(src_path:Path,out_path:Path,phase:str):
    src=Image.open(src_path).convert("RGBA")
    im=src.copy()
    scale=4
    layer=Image.new("RGBA",(im.width*scale,im.height*scale),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    segs=([((470,820),(452,805)),((482,815),(474,792)),((495,817),(494,791))]
          if phase=="hit" else [((482,820),(470,810))])
    for a,b in segs:
        d.line([(a[0]*scale,a[1]*scale),(b[0]*scale,b[1]*scale)],fill=(18,18,18,255),width=4*scale)
    layer=layer.resize(im.size,Image.Resampling.LANCZOS)
    im=Image.alpha_composite(im,layer)
    out_path.parent.mkdir(parents=True,exist_ok=True)
    im.save(out_path)
    return src,im

def metrics(base,candidate):
    diff=ImageChops.difference(base,candidate)
    changed=sum(1 for px in diff.getdata() if px!=(0,0,0,0))
    return {"changedPixelRatio":changed/(base.width*base.height),"diffBBox":diff.getbbox()}

if sha256(BASE_HIT)!=BASE_HIT_SHA:
    raise SystemExit("HT:L hit base SHA mismatch")
if sha256(BASE_REBOUND)!=BASE_REBOUND_SHA:
    raise SystemExit("HT:L rebound base SHA mismatch")

OUT.mkdir(parents=True,exist_ok=True)
QA.mkdir(parents=True,exist_ok=True)
hp=OUT/"bd_ht_rf_l_hit_attempt01.png"
rp=OUT/"bd_ht_rf_l_rebound_attempt01.png"
bh,hit=add_kick(BASE_HIT,hp,"hit")
br,reb=add_kick(BASE_REBOUND,rp,"rebound")
drum=Image.open(DRUM).convert("RGBA")
Image.alpha_composite(drum,hit).save(QA/"hit_composite_attempt01.png")
Image.alpha_composite(drum,reb).save(QA/"rebound_composite_attempt01.png")
result={
  "actionKey":"BD+HT:RF/L",
  "status":"CANDIDATE_VISUAL_QA_REQUIRED",
  "method":"preserve formal HT:L pair exactly; add only the proven deterministic BD kick cue used by M17 BD+LT and M29 BD+HT:RF/R",
  "source":{
    "hit":{"path":str(BASE_HIT.relative_to(ROOT)),"sha256":sha256(BASE_HIT)},
    "rebound":{"path":str(BASE_REBOUND.relative_to(ROOT)),"sha256":sha256(BASE_REBOUND)}
  },
  "hit":{"path":str(hp.relative_to(ROOT)),"sha256":sha256(hp),**metrics(bh,hit)},
  "rebound":{"path":str(rp.relative_to(ROOT)),"sha256":sha256(rp),**metrics(br,reb)}
}
(QA/"build-result-attempt01.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
