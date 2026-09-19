#!/usr/bin/env python3
import argparse,json
from PIL import Image
from common import load_json
from validate_pose import validate_contact,validate_registration

def canvas_size(canvas):
    if isinstance(canvas,dict):
        return (int(canvas["width"]),int(canvas["height"]))
    if isinstance(canvas,(list,tuple)) and len(canvas)==2:
        return (int(canvas[0]),int(canvas[1]))
    raise ValueError("unsupported canvas format")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pose",required=True)
    p.add_argument("--neutral",required=True)
    p.add_argument("--drum",required=True)
    p.add_argument("--candidate",required=True)
    a=p.parse_args()
    q=load_json(a.pose); n=load_json(a.neutral)
    d=Image.open(a.drum).convert("RGBA"); c=Image.open(a.candidate).convert("RGBA")
    expected=canvas_size(q["canvas"])
    same=d.size==c.size==expected
    alpha=c.getchannel("A"); bbox=alpha.getbbox()
    tol=q.get("tolerancesPx",{}).get("effector",q.get("tolerancesPx",{}).get("stickTip",8))
    contact=validate_contact(q,tol,q.get("tolerancesPx",{}).get("reboundSeparation",16))
    reg=validate_registration(q,n,q.get("tolerancesPx",{}).get("stool",12),q.get("tolerancesPx",{}).get("hip",18))
    out={
      "expectedCanvas":list(expected),"drumCanvas":list(d.size),"candidateCanvas":list(c.size),
      "canvasPass":same,"candidateNonEmpty":bbox is not None,"candidateAlphaBbox":list(bbox) if bbox else None,
      "contact":contact,"registration":reg
    }
    out["pass"]=same and bbox is not None and contact["pass"] and reg["pass"]
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
