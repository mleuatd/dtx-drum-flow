#!/usr/bin/env python3
from pathlib import Path
import subprocess, io, json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/history-audit/hh-r-hit"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
COMMITS=[
 ("23e9807cecd23f0afaf6db3764be300e3f83ade0","2026-09-20 promote guarded RD repair"),
 ("205ace87003460c876d48f6e2f4085a354c20c46","2026-09-19 promote guarded motion repair"),
 ("cad6dceb35f341d9a2af0eaf666283ef7fd70a48","2026-09-18 final M1-4 posefix"),
 ("144b2dc2f8f63b0b579163ac1c93cc3581974f7f","2026-09-17 staged import B"),
 ("da466e03e17271b25dc9638a2e412a52a2331a60","2026-09-17 staged import A"),
 ("48fef56a27ec0ad6ccad26ef6070a07fc9eca657","2026-09-17 generated M1-4"),
 ("03b60c420bec041bf54fea916d70f4d22f7a02ed","2026-09-16 reset baseline"),
 ("db3fdcd0b2038b5bb78f59d805472102fc621881","2026-09-16 initial 16m layers")
]
PATH="character-assets/layers/character/hh/hit_r.png"

def rgba_bytes(b):
    with Image.open(io.BytesIO(b)) as im: return np.asarray(im.convert("RGBA")).copy()
def rgba_path(p):
    with Image.open(p) as im: return np.asarray(im.convert("RGBA")).copy()
def alpha_comp(bottom,top):
    b=bottom.astype(float)/255; t=top.astype(float)/255
    ta=t[:,:,3:4]; ba=b[:,:,3:4]; oa=ta+ba*(1-ta)
    rgb=np.divide(t[:,:,:3]*ta+b[:,:,:3]*ba*(1-ta),oa,out=np.zeros_like(b[:,:,:3]),where=oa>0)
    return np.clip(np.rint(np.concatenate([rgb,oa],2)*255),0,255).astype(np.uint8)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    drum=rgba_path(DRUM)
    records=[]; thumbs=[]
    for sha,label in COMMITS:
        try:
            b=subprocess.check_output(["git","show",f"{sha}:{PATH}"],cwd=ROOT)
        except subprocess.CalledProcessError:
            records.append({"commit":sha,"label":label,"present":False}); continue
        person=rgba_bytes(b)
        comp=alpha_comp(drum,person)
        p=OUT/f"{sha[:8]}_hh_r_hit.png"
        c=OUT/f"{sha[:8]}_hh_r_hit_fixed_drum.png"
        Image.fromarray(person,"RGBA").save(p)
        Image.fromarray(comp,"RGBA").save(c)
        thumb=Image.fromarray(comp,"RGBA").convert("RGB").resize((362,272),Image.Resampling.LANCZOS)
        canvas=Image.new("RGB",(362,312),"white"); canvas.paste(thumb,(0,40))
        d=ImageDraw.Draw(canvas)
        d.text((8,6),f"{sha[:8]}  {label}",fill="black")
        thumbs.append(canvas)
        records.append({"commit":sha,"label":label,"present":True,"person":str(p.relative_to(ROOT)),"composite":str(c.relative_to(ROOT))})
    if thumbs:
        cols=2; rows=(len(thumbs)+cols-1)//cols
        sheet=Image.new("RGB",(cols*362,rows*312),(220,220,220))
        for i,im in enumerate(thumbs): sheet.paste(im,((i%cols)*362,(i//cols)*312))
        sheet.save(OUT/"HH_R_HIT_HISTORY_FIXED_DRUM_CONTACT_SHEET.jpg",quality=92)
    (OUT/"HISTORY_INDEX.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"records":len(records),"out":str(OUT.relative_to(ROOT))},ensure_ascii=False))
if __name__=="__main__": main()
