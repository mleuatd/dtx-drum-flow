from __future__ import annotations
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
ROOT=Path(__file__).resolve().parents[1]
CHAR=ROOT/"character-assets/layers/character"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
OUT=ROOT/"character-assets/review-candidates/m136"
QA=ROOT/"character-assets/generated-qa/m136"
P={
 "hit":("ft/hit_r_refresh.png","bf48f08c61d58e20e6a47148e3f34fc70e8b77ef27190a1a85c4e01aa352ba2a"),
 "rebound":("ft/rebound_r_refresh.png","eada124ae96c74ca9f9ffa6144c7f749208f6f6beb3f9ff252368cfebbd924ce")
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add_bd(im,phase):
 s=4;layer=Image.new("RGBA",(im.width*s,im.height*s),(0,0,0,0));d=ImageDraw.Draw(layer)
 seg=[((470,820),(452,805)),((482,815),(474,792)),((495,817),(494,791))] if phase=="hit" else [((482,820),(470,810))]
 for a,b in seg:d.line([(a[0]*s,a[1]*s),(b[0]*s,b[1]*s)],fill=(18,18,18,255),width=4*s)
 return Image.alpha_composite(im,layer.resize(im.size,Image.Resampling.LANCZOS))
def composite(ch):
 drum=Image.open(DRUM).convert("RGBA"); merged=Image.alpha_composite(drum,ch); white=Image.new("RGBA",merged.size,(255,255,255,255));return Image.alpha_composite(white,merged)
OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
res={"schemaVersion":1,"actionKey":"BD+FT:RF/R","method":"formal FT:R exact bytes + proven deterministic BD cue only","phases":{}}
allowed=(438,778,510,836)
for phase,(rel,expected) in P.items():
 src=CHAR/rel
 if sha(src)!=expected:raise SystemExit(f"{phase} source SHA mismatch")
 base=Image.open(src).convert("RGBA");cand=add_bd(base.copy(),phase);out=OUT/f"bd_ft_rf_r_{phase}_attempt01.png";cand.save(out,optimize=False)
 diff=ImageChops.difference(base,cand);bbox=diff.getbbox()
 if bbox is None or not (bbox[0]>=allowed[0] and bbox[1]>=allowed[1] and bbox[2]<=allowed[2] and bbox[3]<=allowed[3]):raise SystemExit(f"{phase} locality fail {bbox}")
 changed=sum(1 for p in diff.getdata() if p!=(0,0,0,0));comp=QA/f"bd_ft_rf_r_{phase}_fixed_drum.png";composite(cand).save(comp)
 res["phases"][phase]={"parentPath":str(src.relative_to(ROOT)),"parentSha256":expected,"candidatePath":str(out.relative_to(ROOT)),"candidateSha256":sha(out),"changedPixels":changed,"changedPixelRatio":changed/(base.width*base.height),"diffBBox":bbox,"locality":"PASS_BD_CUE_ONLY","compositePath":str(comp.relative_to(ROOT))}
(QA/"build-result.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(res,ensure_ascii=False,indent=2))
