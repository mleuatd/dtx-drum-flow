from __future__ import annotations
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ap=argparse.ArgumentParser()
ap.add_argument("--neutral",required=True)
ap.add_argument("--hit",required=True)
ap.add_argument("--rebound",required=True)
ap.add_argument("--drum",required=True)
ap.add_argument("--contacts")
ap.add_argument("--parts",default="")
ap.add_argument("--out-dir",default="qa-preview")
args=ap.parse_args()
out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
def load(p): return Image.open(p).convert("RGBA")
neutral,hit,rebound,drum=map(load,[args.neutral,args.hit,args.rebound,args.drum])
if len({x.size for x in [neutral,hit,rebound,drum]})!=1: raise SystemExit("canvas mismatch")
def composite(char,name):
    c=Image.alpha_composite(drum,char)
    c.save(out/name)
    return c
comps=[composite(neutral,"neutral_composite.png"),composite(hit,"hit_composite.png"),composite(rebound,"rebound_composite.png")]
# Stacked vertical comparison is easier to inspect on narrow/mobile screens.
w,h=comps[0].size
sheet=Image.new("RGBA",(w,h*3),(255,255,255,255))
for i,c in enumerate(comps):sheet.alpha_composite(c,(0,i*h))
sheet.save(out/"neutral_hit_rebound_vertical.png")
if args.contacts:
    data=json.loads(Path(args.contacts).read_text(encoding="utf-8"))
    overlay=comps[1].copy();d=ImageDraw.Draw(overlay)
    for part in [x for x in args.parts.split(",") if x]:
        p=data["parts"].get(part,{})
        xy=p.get("approximate")
        if xy:
            x,y=xy["x"],xy["y"]; d.ellipse((x-18,y-18,x+18,y+18),outline=(255,0,0,255),width=4);d.text((x+22,y-12),part,fill=(255,0,0,255))
        else:
            d.text((20,30+35*len([q for q in args.parts.split(",") if q and q<part])),part+": relative target only",fill=(255,0,0,255))
    overlay.save(out/"hit_contact_overlay.png")
print(json.dumps({"outDir":str(out),"files":[p.name for p in out.iterdir()]},indent=2))
