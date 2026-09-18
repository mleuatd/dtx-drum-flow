from __future__ import annotations
import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"character-assets/layers/character/base/neutral.png"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
OUT_HIT=ROOT/"character-assets/layers/character/lt/hit_r_refresh.png"
OUT_REBOUND=ROOT/"character-assets/layers/character/lt/rebound_r_refresh.png"
QA_DIR=ROOT/"character-assets/generated-qa/m17-lt-r"

BASELINE_SHA="886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9"
HIT_TARGET=(885,455)
REBOUND_TARGET=(900,390)
GRIP=(998,414)

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build(target, out_path):
    src=Image.open(BASE).convert("RGBA")
    im=src.copy()
    # Remove only the old raised right stick above the hand. Core character pixels remain untouched.
    mask=Image.new("L",im.size,0)
    md=ImageDraw.Draw(mask)
    md.polygon([(1018,305),(1037,311),(1008,401),(997,407),(990,397)],fill=255)
    md.ellipse((1016,309,1037,330),fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel("A"),ImageChops.invert(mask)))

    scale=4
    layer=Image.new("RGBA",(im.width*scale,im.height*scale),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    p0=(GRIP[0]*scale,GRIP[1]*scale)
    p1=(target[0]*scale,target[1]*scale)
    d.line([p0,p1],fill=(15,15,15,255),width=11*scale)
    d.line([p0,p1],fill=(248,248,248,255),width=5*scale)
    r=6*scale
    d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(15,15,15,255))
    r2=3*scale
    d.ellipse((p1[0]-r2,p1[1]-r2,p1[0]+r2,p1[1]+r2),fill=(248,248,248,255))
    layer=layer.resize(im.size,Image.Resampling.LANCZOS)
    im=Image.alpha_composite(im,layer)
    out_path.parent.mkdir(parents=True,exist_ok=True)
    im.save(out_path)
    return src,im

def metrics(base,candidate):
    diff=ImageChops.difference(base,candidate)
    changed=sum(1 for px in diff.getdata() if px!=(0,0,0,0))
    return {"changedPixelRatio":changed/(base.width*base.height),"diffBBox":diff.getbbox()}

if sha256(BASE)!=BASELINE_SHA:
    raise SystemExit("baseline SHA mismatch")

base,hit=build(HIT_TARGET,OUT_HIT)
_,rebound=build(REBOUND_TARGET,OUT_REBOUND)
QA_DIR.mkdir(parents=True,exist_ok=True)
drum=Image.open(DRUM).convert("RGBA")
Image.alpha_composite(drum,hit).save(QA_DIR/"hit_composite.png")
Image.alpha_composite(drum,rebound).save(QA_DIR/"rebound_composite.png")
result={
  "baselineSha256":sha256(BASE),
  "hit":{"path":str(OUT_HIT.relative_to(ROOT)),"sha256":sha256(OUT_HIT),**metrics(base,hit)},
  "rebound":{"path":str(OUT_REBOUND.relative_to(ROOT)),"sha256":sha256(OUT_REBOUND),**metrics(base,rebound)},
  "contact":{"part":"LT","hitTarget":{"x":HIT_TARGET[0],"y":HIT_TARGET[1]},"reboundTarget":{"x":REBOUND_TARGET[0],"y":REBOUND_TARGET[1]}},
  "method":"baseline-preserving local stick edit; no face/hair/body/stool redraw"
}
(QA_DIR/"build-result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
