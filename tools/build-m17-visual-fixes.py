from PIL import Image, ImageDraw
from pathlib import Path
import hashlib, json

ROOT=Path(".")
neutral=Image.open(ROOT/"character-assets/layers/character/base/neutral.png").convert("RGBA")

def replace_region_from_neutral(src_path, out_path, box):
    img=Image.open(src_path).convert("RGBA")
    region=neutral.crop(box)
    img.paste(region, box[:2])
    out_path.parent.mkdir(parents=True,exist_ok=True)
    img.save(out_path)
    return img

def build_bdsn(src_kick_path,out_path,end):
    src_kick=Image.open(src_kick_path).convert("RGBA")
    img=neutral.copy()
    # Reuse only the already-approved deterministic BD kick cue from BD+LT.
    img.paste(src_kick.crop((420,730,560,850)),(420,730))
    # Remove the neutral right-stick shaft above the hand; keep hand/body untouched.
    img.paste(Image.new("RGBA",(100,125),(0,0,0,0)),(955,290))
    img.paste(neutral.crop((940,400,1010,470)),(940,400))
    # Add a short inward/downward right-hand stroke. This preserves the locked rear camera
    # and avoids the old front-facing BD+SN pose jump.
    d=ImageDraw.Draw(img)
    start=(968,438)
    d.line([start,end],fill=(20,20,20,255),width=8)
    d.line([start,end],fill=(245,245,245,255),width=4)
    d.line([start,end],fill=(30,30,30,255),width=1)
    r=6
    d.ellipse((end[0]-r,end[1]-r,end[0]+r,end[1]+r),fill=(20,20,20,255))
    d.ellipse((end[0]-3,end[1]-3,end[0]+3,end[1]+3),fill=(245,245,245,255))
    out_path.parent.mkdir(parents=True,exist_ok=True)
    img.save(out_path)
    return img

pairs=[
  ("LT:L","hit",
   ROOT/"character-assets/layers/character/lt/hit_l_refresh.png",
   ROOT/"character-assets/layers/character/lt/hit_l_refresh.png",
   (690,410,1448,510)),
  ("LT:L","rebound",
   ROOT/"character-assets/layers/character/lt/rebound_l_refresh.png",
   ROOT/"character-assets/layers/character/lt/rebound_l_refresh.png",
   (650,400,1448,510)),
  ("FT:L","hit",
   ROOT/"character-assets/layers/character/ft/hit_l_refresh.png",
   ROOT/"character-assets/layers/character/ft/hit_l_refresh.png",
   (725,410,1448,560)),
  ("FT:L","rebound",
   ROOT/"character-assets/layers/character/ft/rebound_l_refresh.png",
   ROOT/"character-assets/layers/character/ft/rebound_l_refresh.png",
   (680,400,1448,550)),
]
results=[]
for action,phase,src,out,box in pairs:
    replace_region_from_neutral(src,out,box)
    raw=out.read_bytes()
    results.append({"actionKey":action,"phase":phase,"path":str(out),"sha256":hashlib.sha256(raw).hexdigest(),"method":"trim overlong left-stick tail by restoring locked neutral pixels; no body/camera/stool redraw"})

for action,phase,src,out,end in [
  ("BD+SN:RF/R","hit",
   ROOT/"character-assets/layers/character/combo/bd_lt_rf_r_hit_refresh.png",
   ROOT/"character-assets/layers/character/combo/bd_sn_rf_r_hit_refresh.png",(800,505)),
  ("BD+SN:RF/R","rebound",
   ROOT/"character-assets/layers/character/combo/bd_lt_rf_r_rebound_refresh.png",
   ROOT/"character-assets/layers/character/combo/bd_sn_rf_r_rebound_refresh.png",(845,470)),
]:
    build_bdsn(src,out,end)
    raw=out.read_bytes()
    results.append({"actionKey":action,"phase":phase,"path":str(out),"sha256":hashlib.sha256(raw).hexdigest(),"method":"locked neutral rear-camera pose + approved BD kick cue + short deterministic right-stick stroke"})

out=ROOT/"character-assets/generated-qa/m17-visual-fix/build-result.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({"schemaVersion":1,"status":"BUILT_RUNTIME_REVIEW_REQUIRED","assets":results},indent=2)+"\n",encoding="utf-8")
print(out.read_text())
