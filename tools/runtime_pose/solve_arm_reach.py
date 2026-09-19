#!/usr/bin/env python3
import argparse,json,math
from common import two_bone_ik
def solve(shoulder,target,upper,forearm,stick,wrist_offset=0,bend=1):
    sx,sy=shoulder; tx,ty=target; dx,dy=tx-sx,ty-sy; d=max(1e-9,math.hypot(dx,dy))
    ux,uy=dx/d,dy/d
    wrist_target=[tx-ux*(stick+wrist_offset),ty-uy*(stick+wrist_offset)]
    ik=two_bone_ik(shoulder,wrist_target,upper,forearm,bend)
    wx,wy=ik["end"]; tip=[wx+ux*(stick+wrist_offset),wy+uy*(stick+wrist_offset)]
    err=math.hypot(tip[0]-tx,tip[1]-ty)
    return {"shoulder":shoulder,"elbow":ik["joint"],"wrist":ik["end"],"stickTip":[round(tip[0],3),round(tip[1],3)],
            "target":target,"tipErrorPx":round(err,3),"reachable":ik["reachable"],"lengths":{"upperArm":upper,"forearm":forearm,"stick":stick,"wristOffset":wrist_offset}}
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--shoulder",nargs=2,type=float,required=True); p.add_argument("--target",nargs=2,type=float,required=True)
    p.add_argument("--upper",type=float,required=True); p.add_argument("--forearm",type=float,required=True); p.add_argument("--stick",type=float,required=True)
    p.add_argument("--wrist-offset",type=float,default=0); p.add_argument("--bend",type=int,choices=(-1,1),default=1)
    a=p.parse_args(); print(json.dumps(solve(a.shoulder,a.target,a.upper,a.forearm,a.stick,a.wrist_offset,a.bend),ensure_ascii=False,indent=2))
