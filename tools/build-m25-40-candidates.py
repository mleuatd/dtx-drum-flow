from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"character-assets/layers/character/base/neutral.png"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
OUT=ROOT/"character-assets/review-candidates/m25_40"
QA=ROOT/"character-assets/generated-qa/m25_40"
BASE_SHA="886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9"
GRIP_R=(998,414); GRIP_L=(735,438)
CONTACT={"HT":(575,360),"RC":(1215,145),"FT":(1165,535),"SN":(420,535)}
REBOUND={"HT:R":(650,330),"HT:L":(650,390),"RC:R":(1110,225)}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def local_stick(src,grip,target):
 im=src.copy(); s=4; layer=Image.new("RGBA",(im.width*s,im.height*s),(0,0,0,0)); d=ImageDraw.Draw(layer)
 p0=(grip[0]*s,grip[1]*s); p1=(target[0]*s,target[1]*s)
 d.line([p0,p1],fill=(15,15,15,255),width=11*s); d.line([p0,p1],fill=(248,248,248,255),width=5*s)
 r=6*s; d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(15,15,15,255))
 r=3*s; d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(248,248,248,255))
 return Image.alpha_composite(im,layer.resize(im.size,Image.Resampling.LANCZOS))
def save_pair(action,hit_target,rebound_target,grip=GRIP_R):
 base=Image.open(BASE).convert("RGBA"); key=action.lower().replace("+","_").replace(":","_").replace("/","_")
 hp=OUT/f"{key}_hit_attempt01.png"; rp=OUT/f"{key}_rebound_attempt01.png"
 hit=local_stick(base,grip,hit_target); reb=local_stick(base,grip,rebound_target)
 OUT.mkdir(parents=True,exist_ok=True); hp.parent.mkdir(parents=True,exist_ok=True); hit.save(hp); reb.save(rp)
 q=QA/key; q.mkdir(parents=True,exist_ok=True); drum=Image.open(DRUM).convert("RGBA")
 Image.alpha_composite(drum,hit).save(q/"hit_composite.png"); Image.alpha_composite(drum,reb).save(q/"rebound_composite.png")
 res={"actionKey":action,"status":"CANDIDATE_VISUAL_QA_REQUIRED","sourceSha256":sha(BASE),"hit":{"path":str(hp.relative_to(ROOT)),"sha256":sha(hp)},"rebound":{"path":str(rp.relative_to(ROOT)),"sha256":sha(rp)}}
 (q/"build-result.json").write_text(json.dumps(res,indent=2)+"\n"); return res
if sha(BASE)!=BASE_SHA: raise SystemExit("neutral SHA mismatch")
actions=sys.argv[1:] or ["HT:R","HT:L","RC:R"]
results=[]
for a in actions:
 if a=="HT:R": results.append(save_pair(a,CONTACT["HT"],REBOUND[a],GRIP_R))
 elif a=="HT:L": results.append(save_pair(a,CONTACT["HT"],REBOUND[a],GRIP_L))
 elif a=="RC:R": results.append(save_pair(a,CONTACT["RC"],REBOUND[a],GRIP_R))
 else: raise SystemExit("unsupported action "+a)
print(json.dumps(results,indent=2))
