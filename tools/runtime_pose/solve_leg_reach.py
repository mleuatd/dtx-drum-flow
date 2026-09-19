#!/usr/bin/env python3
import argparse,json,math
from common import two_bone_ik
def solve(hip,target,thigh,shin,foot=0,bend=1):
    hx,hy=hip; tx,ty=target; dx,dy=tx-hx,ty-hy; d=max(1e-9,math.hypot(dx,dy)); ux,uy=dx/d,dy/d
    ankle_target=[tx-ux*foot,ty-uy*foot]; ik=two_bone_ik(hip,ankle_target,thigh,shin,bend)
    ax,ay=ik["end"]; toe=[ax+ux*foot,ay+uy*foot]; err=math.hypot(toe[0]-tx,toe[1]-ty)
    return {"hip":hip,"knee":ik["joint"],"ankle":ik["end"],"footTarget":[round(toe[0],3),round(toe[1],3)],"pedalTarget":target,
            "pedalErrorPx":round(err,3),"reachable":ik["reachable"],"lengths":{"thigh":thigh,"shin":shin,"foot":foot}}
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--hip",nargs=2,type=float,required=True); p.add_argument("--target",nargs=2,type=float,required=True)
    p.add_argument("--thigh",type=float,required=True); p.add_argument("--shin",type=float,required=True); p.add_argument("--foot",type=float,default=0); p.add_argument("--bend",type=int,choices=(-1,1),default=1)
    a=p.parse_args(); print(json.dumps(solve(a.hip,a.target,a.thigh,a.shin,a.foot,a.bend),ensure_ascii=False,indent=2))
