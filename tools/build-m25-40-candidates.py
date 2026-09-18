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
APPROVED={
 "FT:R":{
  "hit":("character-assets/layers/character/ft/hit_r_refresh.png","bf48f08c61d58e20e6a47148e3f34fc70e8b77ef27190a1a85c4e01aa352ba2a"),
  "rebound":("character-assets/layers/character/ft/rebound_r_refresh.png","eada124ae96c74ca9f9ffa6144c7f749208f6f6beb3f9ff252368cfebbd924ce")
 },
 "SN:L":{
  "hit":("character-assets/layers/character/sn/hit_l.png","9941584d670ac6441b8853c8c191318aff7482264f81b6473fa1a3e381cd4cfb"),
  "rebound":("character-assets/layers/character/sn/rebound_l.png","79484f0681273bb86b3ea9e56514cb9aa822945c6dc4b086d3e7093cbf25c777")
 }
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def local_stick(src,grip,target):
 im=src.copy(); s=4; layer=Image.new("RGBA",(im.width*s,im.height*s),(0,0,0,0)); d=ImageDraw.Draw(layer)
 p0=(grip[0]*s,grip[1]*s); p1=(target[0]*s,target[1]*s)
 d.line([p0,p1],fill=(15,15,15,255),width=11*s); d.line([p0,p1],fill=(248,248,248,255),width=5*s)
 r=6*s; d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(15,15,15,255))
 r=3*s; d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(248,248,248,255))
 return Image.alpha_composite(im,layer.resize(im.size,Image.Resampling.LANCZOS))
def save_outputs(action,hit,reb,extra=None):
 key=action.lower().replace("+","_").replace(":","_").replace("/","_")
 hp=OUT/f"{key}_hit_attempt01.png"; rp=OUT/f"{key}_rebound_attempt01.png"
 OUT.mkdir(parents=True,exist_ok=True); hp.parent.mkdir(parents=True,exist_ok=True); hit.save(hp); reb.save(rp)
 q=QA/key; q.mkdir(parents=True,exist_ok=True); drum=Image.open(DRUM).convert("RGBA")
 Image.alpha_composite(drum,hit).save(q/"hit_composite.png"); Image.alpha_composite(drum,reb).save(q/"rebound_composite.png")
 res={"actionKey":action,"status":"CANDIDATE_VISUAL_QA_REQUIRED","sourceSha256":sha(BASE),
      "hit":{"path":str(hp.relative_to(ROOT)),"sha256":sha(hp)},
      "rebound":{"path":str(rp.relative_to(ROOT)),"sha256":sha(rp)}}
 if extra: res.update(extra)
 (q/"build-result.json").write_text(json.dumps(res,indent=2)+"\n"); return res
def save_pair(action,hit_target,rebound_target,grip=GRIP_R):
 base=Image.open(BASE).convert("RGBA")
 return save_outputs(action,local_stick(base,grip,hit_target),local_stick(base,grip,rebound_target))
def approved_image(action,phase):
 rel,expected=APPROVED[action][phase]; p=ROOT/rel
 actual=sha(p)
 if actual!=expected: raise SystemExit(f"approved source SHA mismatch {action} {phase}: {actual}")
 return Image.open(p).convert("RGBA"),rel,actual
def merge_on_neutral(images):
 base=Image.open(BASE).convert("RGBA"); out=base.copy()
 for src in images:
  diff=ImageChops.difference(base,src)
  mask=diff.getchannel("R").point(lambda v:255 if v else 0)
  for ch in ("G","B","A"):
   mask=ImageChops.lighter(mask,diff.getchannel(ch).point(lambda v:255 if v else 0))
  out.paste(src,(0,0),mask)
 return out
def save_ft_sn():
 fh,fhp,fhs=approved_image("FT:R","hit"); sh,shp,shs=approved_image("SN:L","hit")
 fr,frp,frs=approved_image("FT:R","rebound"); sr,srp,srs=approved_image("SN:L","rebound")
 hit=merge_on_neutral([fh,sh]); reb=merge_on_neutral([fr,sr])
 return save_outputs("FT+SN:R/L",hit,reb,{
  "method":"merge approved FT:R and SN:L neutral deltas only",
  "approvedParents":{"hit":[{"path":fhp,"sha256":fhs},{"path":shp,"sha256":shs}],
                     "rebound":[{"path":frp,"sha256":frs},{"path":srp,"sha256":srs}]}
 })
if sha(BASE)!=BASE_SHA: raise SystemExit("neutral SHA mismatch")
actions=sys.argv[1:] or ["HT:R","HT:L","RC:R","FT+SN:R/L"]
results=[]
for a in actions:
 if a=="HT:R": results.append(save_pair(a,CONTACT["HT"],REBOUND[a],GRIP_R))
 elif a=="HT:L": results.append(save_pair(a,CONTACT["HT"],REBOUND[a],GRIP_L))
 elif a=="RC:R": results.append(save_pair(a,CONTACT["RC"],REBOUND[a],GRIP_R))
 elif a=="FT+SN:R/L": results.append(save_ft_sn())
 else: raise SystemExit("unsupported action "+a)
print(json.dumps(results,indent=2))

# retrigger-ft-sn-2026-09-19-0848-jst
