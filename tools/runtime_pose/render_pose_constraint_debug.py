#!/usr/bin/env python3
import argparse
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
    effectors=q.get("effectors")
    if effectors is None:
        effectors=[]
        if q.get("contactPoint"):
            effectors.append({"target":q.get("contactPoint"),"point":q.get("stickTip"),"kind":"stick"})
    for e in effectors:
        target=e.get("target"); point=e.get("point")
        if target:
            draw.ellipse((target[0]-8,target[1]-8,target[0]+8,target[1]+8),outline=(255,0,0,255),width=3)
        if point:
            draw.ellipse((point[0]-5,point[1]-5,point[0]+5,point[1]+5),outline=(0,0,255,255),width=2)
        if target and point:
            draw.line([point,target],fill=(255,0,0,255),width=2)
    if a.candidate: base=Image.alpha_composite(base,Image.open(a.candidate).convert("RGBA"))
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); base.save(a.output)
if __name__=="__main__": main()
