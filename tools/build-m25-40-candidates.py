from __future__ import annotations
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"character-assets/layers/character/base/neutral.png"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
OUT=ROOT/"character-assets/review-candidates/m25_40"
QA=ROOT/"character-assets/generated-qa/m25_40/ht_r"
BASE_SHA="886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9"
GRIP=(998,414)
HIT=(575,360)
REBOUND=(650,330)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def build(target,out):
    src=Image.open(BASE).convert("RGBA")
    im=src.copy()
    # Same approved local-stick method used by M17 LT:R. Remove only the old raised right stick.
    mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask)
    d.polygon([(1018,305),(1037,311),(1008,401),(997,407),(990,397)],fill=255)
    d.ellipse((1016,309,1037,330),fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel("A"),ImageChops.invert(mask)))
    s=4; layer=Image.new("RGBA",(im.width*s,im.height*s),(0,0,0,0)); d=ImageDraw.Draw(layer)
    p0=(GRIP[0]*s,GRIP[1]*s); p1=(target[0]*s,target[1]*s)
    d.line([p0,p1],fill=(15,15,15,255),width=11*s)
    d.line([p0,p1],fill=(248,248,248,255),width=5*s)
    r=6*s; d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(15,15,15,255))
    r=3*s; d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(248,248,248,255))
    im=Image.alpha_composite(im,layer.resize(im.size,Image.Resampling.LANCZOS))
    out.parent.mkdir(parents=True,exist_ok=True); im.save(out)
    return src,im

if sha(BASE)!=BASE_SHA: raise SystemExit("neutral SHA mismatch")
OUT.mkdir(parents=True,exist_ok=True); QA.mkdir(parents=True,exist_ok=True)
hp=OUT/"ht_r_hit_attempt01.png"; rp=OUT/"ht_r_rebound_attempt01.png"
base,hit=build(HIT,hp); _,reb=build(REBOUND,rp)
drum=Image.open(DRUM).convert("RGBA")
Image.alpha_composite(drum,hit).save(QA/"hit_composite.png")
Image.alpha_composite(drum,reb).save(QA/"rebound_composite.png")
def metrics(c):
    diff=ImageChops.difference(base,c); changed=sum(1 for px in diff.getdata() if px!=(0,0,0,0))
    return {"changedPixelRatio":changed/(base.width*base.height),"diffBBox":diff.getbbox()}
result={"schemaVersion":1,"status":"CANDIDATE_VISUAL_QA_REQUIRED","actionKey":"HT:R","method":"approved M17 baseline-preserving local right-stick edit","source":{"path":str(BASE.relative_to(ROOT)),"sha256":sha(BASE)},"hit":{"path":str(hp.relative_to(ROOT)),"sha256":sha(hp),**metrics(hit)},"rebound":{"path":str(rp.relative_to(ROOT)),"sha256":sha(rp),**metrics(reb)},"contact":{"part":"HT","hit":{"x":575,"y":360},"rebound":{"x":650,"y":330}}}
(QA/"build-result.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
