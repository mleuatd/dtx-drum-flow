from __future__ import annotations
import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT=Path(__file__).resolve().parents[1]
CHAR=ROOT/"character-assets/layers/character"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
OUT=ROOT/"character-assets/review-candidates/m105_106"
QA=ROOT/"character-assets/generated-qa/m105_106"

PAIRS={
 "bd_ft_sn_rf_r_l":{
   "actionKey":"BD+FT+SN:RF/R/L",
   "hit":("combo/ft_sn_r_l_hit_refresh.png","46f930ce4e2e14476ec64d53812a8f839954eb840d757831faa89bf3910162f2"),
   "rebound":("combo/ft_sn_r_l_rebound_refresh.png","5cda451c8b81975c3cc00d9a00e93c0875b6fe6b51a0641439dbc7d0cddc5aeb"),
 },
 "bd_ft_rf_l":{
   "actionKey":"BD+FT:RF/L",
   "hit":("ft/hit_l_refresh.png","6d89ab051f7ac08e1f9fb59ab54cbc6c7451755e62c73a2492c419db1054366e"),
   "rebound":("ft/rebound_l_refresh.png","4c5bba2ad09940bc858b945f8442af6b709c3d7e7d155b03ba26fb130efa8419"),
 }
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def add_bd(im,phase):
 s=4
 layer=Image.new("RGBA",(im.width*s,im.height*s),(0,0,0,0))
 d=ImageDraw.Draw(layer)
 seg=[((470,820),(452,805)),((482,815),(474,792)),((495,817),(494,791))] if phase=="hit" else [((482,820),(470,810))]
 for a,b in seg:
  d.line([(a[0]*s,a[1]*s),(b[0]*s,b[1]*s)],fill=(18,18,18,255),width=4*s)
 return Image.alpha_composite(im,layer.resize(im.size,Image.Resampling.LANCZOS))

def composite(ch):
 drum=Image.open(DRUM).convert("RGBA")
 if drum.size!=ch.size: raise SystemExit("drum size mismatch")
 merged=Image.alpha_composite(drum,ch)
 white=Image.new("RGBA",merged.size,(255,255,255,255))
 return Image.alpha_composite(white,merged)

OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
result={"schemaVersion":1,"method":"formal parent exact bytes + proven deterministic BD cue only","pairs":{}}
allowed=(438,778,510,836)
for key,spec in PAIRS.items():
 result["pairs"][key]={"actionKey":spec["actionKey"],"phases":{}}
 for phase in ("hit","rebound"):
  rel,expected=spec[phase]
  src=CHAR/rel
  actual=sha(src)
  if actual!=expected: raise SystemExit(f"{key} {phase} source SHA mismatch {actual}")
  base=Image.open(src).convert("RGBA")
  if base.size!=(1448,1086): raise SystemExit(f"{key} {phase} size mismatch")
  cand=add_bd(base.copy(),phase)
  out=OUT/f"{key}_{phase}_attempt01.png"; cand.save(out,optimize=False)
  diff=ImageChops.difference(base,cand); bbox=diff.getbbox()
  if bbox is None: raise SystemExit(f"{key} {phase}: no change")
  if not (bbox[0]>=allowed[0] and bbox[1]>=allowed[1] and bbox[2]<=allowed[2] and bbox[3]<=allowed[3]):
   raise SystemExit(f"{key} {phase}: diff escaped BD region {bbox}")
  changed=sum(1 for p in diff.getdata() if p!=(0,0,0,0))
  comp=QA/f"{key}_{phase}_fixed_drum.png"; composite(cand).save(comp)
  result["pairs"][key]["phases"][phase]={
    "parentPath":str(src.relative_to(ROOT)),"parentSha256":expected,
    "candidatePath":str(out.relative_to(ROOT)),"candidateSha256":sha(out),
    "changedPixels":changed,"changedPixelRatio":changed/(base.width*base.height),
    "diffBBox":bbox,"locality":"PASS_BD_CUE_ONLY","compositePath":str(comp.relative_to(ROOT))
  }
(QA/"build-result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
