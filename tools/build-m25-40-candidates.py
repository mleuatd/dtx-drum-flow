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
GRIP_R=(998,414); GRIP_L=(500,480)
CONTACT={"HT":(575,360),"RC":(1215,145),"FT":(1165,535),"SN":(420,535)}
REBOUND={"HT:R":(650,330),"HT:L":(650,390),"RC:R":(1110,225)}
HT_R_PARENT={
 "hit":("character-assets/layers/character/lt/hit_r_refresh.png","b78b91006a445933036c36896972840d165c2c2afb09028b4baf0a3da5fbeb72"),
 "rebound":("character-assets/layers/character/lt/rebound_r_refresh.png","d86b25997cb77623f71793eab97adcb74dc0d60a8fa9519b943afa25758727bf")
}
LIMB_LOCAL_FT_SN={
 "hit":("character-assets/candidates/m25_28/ft_sn_r_l_hit_attempt03.png","0aea2d5072ecb5745f19f1ff5e35cdecfb1a45ec6117a38823d7d31df7a3b1d6"),
 "rebound":("character-assets/candidates/m25_28/ft_sn_r_l_rebound_attempt03.png","44f7e79110c1c7a2fb9aff757d1142a0e700a712de009a25dbf9adb9e39eb9c8")
}
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
def erase_original_stick(im,grip):
 # Locked neutral already contains one stick per hand. Remove only the exposed shaft
 # before drawing a replacement; keep a safety margin around the hand itself.
 out=im.copy(); alpha=out.getchannel("A"); cut=Image.new("L",out.size,0); d=ImageDraw.Draw(cut)
 if grip==GRIP_R:
  d.line([(1004,386),(1026,316)],fill=255,width=30)
 else:
  d.line([(487,451),(430,386)],fill=255,width=30)
 alpha=ImageChops.subtract(alpha,cut)
 out.putalpha(alpha)
 return out
def local_stick(src,grip,target):
 im=erase_original_stick(src,grip); s=4; layer=Image.new("RGBA",(im.width*s,im.height*s),(0,0,0,0)); d=ImageDraw.Draw(layer)
 p0=(grip[0]*s,grip[1]*s); p1=(target[0]*s,target[1]*s)
 d.line([p0,p1],fill=(15,15,15,255),width=11*s); d.line([p0,p1],fill=(248,248,248,255),width=5*s)
 r=6*s; d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(15,15,15,255))
 r=3*s; d.ellipse((p1[0]-r,p1[1]-r,p1[0]+r,p1[1]+r),fill=(248,248,248,255))
 return Image.alpha_composite(im,layer.resize(im.size,Image.Resampling.LANCZOS))
def save_outputs(action,hit,reb,extra=None):
 key=action.lower().replace("+","_").replace(":","_").replace("/","_")
 hp=OUT/f"{key}_hit_attempt03.png"; rp=OUT/f"{key}_rebound_attempt02.png"
 OUT.mkdir(parents=True,exist_ok=True); hp.parent.mkdir(parents=True,exist_ok=True); hit.save(hp); reb.save(rp)
 q=QA/key; q.mkdir(parents=True,exist_ok=True); drum=Image.open(DRUM).convert("RGBA")
 Image.alpha_composite(drum,hit).save(q/"hit_composite.png"); Image.alpha_composite(drum,reb).save(q/"rebound_composite.png")
 res={"actionKey":action,"status":"CANDIDATE_VISUAL_QA_REQUIRED","sourceSha256":sha(BASE),
      "hit":{"path":str(hp.relative_to(ROOT)),"sha256":sha(hp)},
      "rebound":{"path":str(rp.relative_to(ROOT)),"sha256":sha(rp)}}
 if extra: res.update(extra)
 (q/"build-result.json").write_text(json.dumps(res,indent=2)+"\n"); return res
def save_ht_r_arm_local():
 # Attempt04 changes strategy after repeated long-stick failures:
 # start from the live-QA-passed LT:R arm/hand/stick pose, then retarget only
 # the exposed stick endpoint to HT. This keeps a naturally relocated right arm.
 imgs=[]; parents=[]
 for phase,target in (("hit",CONTACT["HT"]),("rebound",REBOUND["HT:R"])):
  rel,expected=HT_R_PARENT[phase]; p=ROOT/rel; actual=sha(p)
  if actual!=expected: raise SystemExit(f"HT:R parent SHA mismatch {phase}: {actual}")
  src=Image.open(p).convert("RGBA")
  # Preserve the approved relocated arm/hand. Remove only the LT-side exposed
  # shaft near its old target, then draw a short retargeted shaft from the
  # approved hand neighborhood rather than from neutral.
  out=src.copy(); alpha=out.getchannel("A"); cut=Image.new("L",out.size,0); d=ImageDraw.Draw(cut)
  d.line([(850,430),(900,470)],fill=255,width=34); alpha=ImageChops.subtract(alpha,cut); out.putalpha(alpha)
  # LT:R approved hand is already forward; use a forward grip anchor to avoid
  # the cross-body neutral-stick geometry that failed attempts 01-03.
  # Draw directly from the approved forward hand anchor. Do not call the
  # neutral-stick eraser because this anchor is intentionally not GRIP_R/L.
  ss=4; layer=Image.new("RGBA",(out.width*ss,out.height*ss),(0,0,0,0)); dd=ImageDraw.Draw(layer)
  grip=(760,410); p0=(grip[0]*ss,grip[1]*ss); p1=(target[0]*ss,target[1]*ss)
  dd.line([p0,p1],fill=(15,15,15,255),width=11*ss); dd.line([p0,p1],fill=(248,248,248,255),width=5*ss)
  rr=6*ss; dd.ellipse((p1[0]-rr,p1[1]-rr,p1[0]+rr,p1[1]+rr),fill=(15,15,15,255))
  rr=3*ss; dd.ellipse((p1[0]-rr,p1[1]-rr,p1[0]+rr,p1[1]+rr),fill=(248,248,248,255))
  out=Image.alpha_composite(out,layer.resize(out.size,Image.Resampling.LANCZOS))
  imgs.append(out); parents.append({"path":rel,"sha256":actual})
 key="ht_r"; OUT.mkdir(parents=True,exist_ok=True)
 hp=OUT/"ht_r_hit_attempt04.png"; rp=OUT/"ht_r_rebound_attempt04.png"; imgs[0].save(hp); imgs[1].save(rp)
 q=QA/key; q.mkdir(parents=True,exist_ok=True); drum=Image.open(DRUM).convert("RGBA")
 Image.alpha_composite(drum,imgs[0]).save(q/"hit_composite_attempt04.png")
 Image.alpha_composite(drum,imgs[1]).save(q/"rebound_composite_attempt04.png")
 res={"actionKey":"HT:R","status":"CANDIDATE_VISUAL_QA_REQUIRED","method":"arm-local LT:R live-QA parent retarget","approvedParents":parents,
      "hit":{"path":str(hp.relative_to(ROOT)),"sha256":sha(hp)},"rebound":{"path":str(rp.relative_to(ROOT)),"sha256":sha(rp)}}
 (q/"build-result-attempt04.json").write_text(json.dumps(res,indent=2)+"\n"); return res
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
 # Prefer the already QA'd locked-baseline limb-local pair once it is imported.
 imgs=[]; parents=[]
 for phase in ("hit","rebound"):
  rel,expected=LIMB_LOCAL_FT_SN[phase]; p=ROOT/rel
  if p.exists():
   actual=sha(p)
   if actual!=expected: raise SystemExit(f"limb-local FT+SN SHA mismatch {phase}: {actual}")
   imgs.append(Image.open(p).convert("RGBA")); parents.append({"path":rel,"sha256":actual})
  else:
   # Fallback only for development; visual QA must reject whole-image baseline drift.
   fa,fp,fs=approved_image("FT:R",phase); sa,sp,ss=approved_image("SN:L",phase)
   imgs.append(merge_on_neutral([fa,sa])); parents.append({"fallback":[fp,sp],"sha256":[fs,ss]})
 return save_outputs("FT+SN:R/L",imgs[0],imgs[1],{"method":"locked-baseline limb-local pair when imported","approvedParents":parents})
if sha(BASE)!=BASE_SHA: raise SystemExit("neutral SHA mismatch")
actions=sys.argv[1:] or ["HT:R","HT:L","RC:R","FT+SN:R/L"]
results=[]
for a in actions:
 if a=="HT:R": results.append(save_ht_r_arm_local())
 elif a=="HT:L": results.append(save_pair(a,CONTACT["HT"],REBOUND[a],GRIP_L))
 elif a=="RC:R": results.append(save_pair(a,CONTACT["RC"],REBOUND[a],GRIP_R))
 elif a=="FT+SN:R/L": results.append(save_ft_sn())
 else: raise SystemExit("unsupported action "+a)
print(json.dumps(results,indent=2))

# retrigger-ft-sn-2026-09-19-0848-jst
