#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from common import load_json
def main():
    p=argparse.ArgumentParser(); p.add_argument("--pose",required=True); p.add_argument("--drum",required=True); p.add_argument("--candidate"); p.add_argument("--output",required=True); a=p.parse_args()
    q=load_json(a.pose); base=Image.open(a.drum).convert("RGBA"); draw=ImageDraw.Draw(base)
    for name,pt in q.get("joints",{}).items():
        if isinstance(pt,list) and len(pt)==2: draw.ellipse((pt[0]-4,pt[1]-4,pt[0]+4,pt[1]+4),outline=(0,0,0,255),width=2)
    pairs=[("shoulder_l","elbow_l"),("elbow_l","wrist_l"),("shoulder_r","elbow_r"),("elbow_r","wrist_r"),("hip_l","knee_l"),("knee_l","ankle_l"),("hip_r","knee_r"),("knee_r","ankle_r")]
    for x,y in pairs:
        if x in q["joints"] and y in q["joints"]: draw.line([q["joints"][x],q["joints"][y]],fill=(0,0,0,255),width=2)
    if q.get("contactPoint"): draw.ellipse((q["contactPoint"][0]-8,q["contactPoint"][1]-8,q["contactPoint"][0]+8,q["contactPoint"][1]+8),outline=(255,0,0,255),width=3)
    if q.get("stickTip") and q.get("contactPoint"): draw.line([q["stickTip"],q["contactPoint"]],fill=(255,0,0,255),width=2)
    if a.candidate: base=Image.alpha_composite(base,Image.open(a.candidate).convert("RGBA"))
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); base.save(a.output)
if __name__=="__main__": main()
