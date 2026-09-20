#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/static-body-atlas"
OUT.mkdir(parents=True,exist_ok=True)
neutral=Image.open(ROOT/"character-assets/layers/character/base/neutral.png").convert("RGBA")
files=[]
for sub in ("rc","rd","ht","lt","ft","sn","bd","hh"):
    for p in sorted((ROOT/f"character-assets/layers/character/{sub}").glob("*.png")):
        files.append(p)
crop=(850,250,1100,560)
# External ghost area; lower occupancy is preferred, but central hair preservation is separately measured.
ghost=(960,300,1080,490)
hair=(850,300,970,560)
N=neutral
rows=[]
thumbs=[]
for p in files:
    im=Image.open(p).convert("RGBA")
    if im.size!=neutral.size: continue
    g=im.crop(ghost); h=im.crop(hair); nh=neutral.crop(hair)
    ga=g.getchannel("A")
    ghost_opaque=sum(1 for v in ga.getdata() if v>64)
    # Hair-region exact match ratio to neutral favors static registration.
    ia=list(h.getdata()); na=list(nh.getdata())
    exact=sum(1 for a,b in zip(ia,na) if a==b)
    hair_exact=exact/max(1,len(ia))
    cp=im.crop(crop)
    bg=Image.new("RGB",cp.size,"white");bg.paste(cp,mask=cp.getchannel("A"))
    thumbs.append((str(p.relative_to(ROOT)),bg))
    rows.append({"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"ghostOpaquePixels":ghost_opaque,"hairExactToNeutral":round(hair_exact,4)})
rows.sort(key=lambda x:(x["ghostOpaquePixels"],-x["hairExactToNeutral"]))
cols=4;cw,ch=250,345
sheet=Image.new("RGB",(cols*cw,((len(thumbs)+cols-1)//cols)*ch),"white");d=ImageDraw.Draw(sheet)
for i,(name,img) in enumerate(thumbs):
    x=(i%cols)*cw;y=(i//cols)*ch
    sheet.paste(img,(x,y));d.text((x+3,y+312),name.replace("character-assets/layers/character/",""),fill="black")
sheet.save(OUT/"right_hair_donor_atlas.jpg",quality=94)
(OUT/"ranking.json").write_text(json.dumps({"crop":crop,"ghostRegion":ghost,"hairRegion":hair,"ranking":rows},indent=2)+"\n")
print(json.dumps(rows[:8],indent=2))
