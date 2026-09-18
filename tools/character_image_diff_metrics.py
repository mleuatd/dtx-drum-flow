from __future__ import annotations
import argparse,json
from pathlib import Path
from PIL import Image,ImageChops
def bbox(im): return im.getchannel("A").getbbox()
def center(bb): return None if not bb else [(bb[0]+bb[2])/2,(bb[1]+bb[3])/2]
def metric(a,b):
    a,b=a.convert("RGBA"),b.convert("RGBA")
    d=ImageChops.difference(a,b);changed=sum(1 for px in d.getdata() if px!=(0,0,0,0));total=a.width*a.height
    ba,bb=bbox(a),bbox(b);ca,cb=center(ba),center(bb)
    shift=None if not ca or not cb else ((ca[0]-cb[0])**2+(ca[1]-cb[1])**2)**.5
    return {"changedPixelRatio":changed/total,"bboxA":ba,"bboxB":bb,"bboxCenterShiftPx":shift}
ap=argparse.ArgumentParser();ap.add_argument("neutral");ap.add_argument("hit");ap.add_argument("rebound");ap.add_argument("--out",default="image-diff-metrics.json");args=ap.parse_args()
n,h,r=[Image.open(x) for x in [args.neutral,args.hit,args.rebound]]
out={"neutralToHit":metric(n,h),"hitToRebound":metric(h,r),"reboundToNeutral":metric(r,n),"policy":"metrics are WARN/support signals, never automatic visual approval"}
Path(args.out).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8");print(json.dumps(out,indent=2))
