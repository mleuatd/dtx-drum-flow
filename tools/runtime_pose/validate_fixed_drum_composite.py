#!/usr/bin/env python3
import argparse,json,math
from PIL import Image
from common import load_json
from validate_pose import validate_contact,validate_registration
def main():
    p=argparse.ArgumentParser(); p.add_argument("--pose",required=True); p.add_argument("--neutral",required=True); p.add_argument("--drum",required=True); p.add_argument("--candidate",required=True); a=p.parse_args()
    q=load_json(a.pose); n=load_json(a.neutral); d=Image.open(a.drum).convert("RGBA"); c=Image.open(a.candidate).convert("RGBA")
    same=d.size==c.size==tuple(q["canvas"]); alpha=c.getchannel("A"); bbox=alpha.getbbox()
    contact=validate_contact(q,q.get("tolerancesPx",{}).get("stickTip",8)); reg=validate_registration(q,n,q.get("tolerancesPx",{}).get("stool",12),q.get("tolerancesPx",{}).get("hip",18))
    out={"canvasPass":same,"candidateNonEmpty":bbox is not None,"contact":contact,"registration":reg}
    out["pass"]=same and bbox is not None and contact["pass"] and reg["pass"]; print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
