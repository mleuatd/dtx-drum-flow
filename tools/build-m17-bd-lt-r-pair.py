from __future__ import annotations
import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE_HIT=ROOT/"character-assets/layers/character/lt/hit_r_refresh.png"
BASE_REBOUND=ROOT/"character-assets/layers/character/lt/rebound_r_refresh.png"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
OUT_HIT=ROOT/"character-assets/layers/character/combo/bd_lt_rf_r_hit_refresh.png"
OUT_REBOUND=ROOT/"character-assets/layers/character/combo/bd_lt_rf_r_rebound_refresh.png"
QA_DIR=ROOT/"character-assets/generated-qa/m17-bd-lt-r"

BASE_HIT_SHA="b78b91006a445933036c36896972840d165c2c2afb09028b4baf0a3da5fbeb72"
BASE_REBOUND_SHA="d86b25997cb77623f71793eab97adcb74dc0d60a8fa9519b943afa25758727bf"

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add_kick(src_path:Path,out_path:Path,phase:str):
    src=Image.open(src_path).convert("RGBA")
    im=src.copy()
    scale=4
    layer=Image.new("RGBA",(im.width*scale,im.height*scale),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    segs=(
      [((470,820),(452,805)),((482,815),(474,792)),((495,817),(494,791))]
      if phase=="hit" else
      [((482,820),(470,810))]
    )
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
    raise SystemExit("LT:R hit base SHA mismatch")
if sha256(BASE_REBOUND)!=BASE_REBOUND_SHA:
    raise SystemExit("LT:R rebound base SHA mismatch")

base_hit,hit=add_kick(BASE_HIT,OUT_HIT,"hit")
base_rebound,rebound=add_kick(BASE_REBOUND,OUT_REBOUND,"rebound")
QA_DIR.mkdir(parents=True,exist_ok=True)
drum=Image.open(DRUM).convert("RGBA")
Image.alpha_composite(drum,hit).save(QA_DIR/"hit_composite.png")
Image.alpha_composite(drum,rebound).save(QA_DIR/"rebound_composite.png")
result={
  "source":{
    "hit":{"path":str(BASE_HIT.relative_to(ROOT)),"sha256":sha256(BASE_HIT)},
    "rebound":{"path":str(BASE_REBOUND.relative_to(ROOT)),"sha256":sha256(BASE_REBOUND)}
  },
  "hit":{"path":str(OUT_HIT.relative_to(ROOT)),"sha256":sha256(OUT_HIT),**metrics(base_hit,hit)},
  "rebound":{"path":str(OUT_REBOUND.relative_to(ROOT)),"sha256":sha256(OUT_REBOUND),**metrics(base_rebound,rebound)},
  "method":"preserve approved LT:R pair exactly; add deterministic local BD kick cue only"
}
(QA_DIR/"build-result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
