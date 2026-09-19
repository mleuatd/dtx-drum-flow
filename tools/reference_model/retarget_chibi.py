#!/usr/bin/env python3
import argparse, json, math
from pathlib import Path
JOINTS=['head_top','chin','neck','shoulder_l','shoulder_r','elbow_l','elbow_r','wrist_l','wrist_r','hip_l','hip_r','knee_l','knee_r','ankle_l','ankle_r']
def pt(p): return [float(p[0]),float(p[1])]
def mid(a,b): return [(a[0]+b[0])/2,(a[1]+b[1])/2]
def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',required=True); ap.add_argument('--pose',required=True); ap.add_argument('--output',required=True)
    ap.add_argument('--target-head-count',type=float,default=4.0)
    args=ap.parse_args()
    model=json.loads(Path(args.model).read_text()); pose=json.loads(Path(args.pose).read_text())
    j={k:pt(v) for k,v in pose['joints'].items() if k in JOINTS}
    for req in ['head_top','chin','shoulder_l','shoulder_r','hip_l','hip_r','ankle_l','ankle_r']:
        if req not in j: raise SystemExit(f'missing joint {req}')
    head=dist(j['head_top'],j['chin']); body_top=j['head_top'][1]
    feet=max(j['ankle_l'][1],j['ankle_r'][1]); height=max(1e-6,feet-body_top)
    current_heads=height/max(head,1e-6)
    desired_height=head*args.target_head_count
    below=max(1e-6,height-head); desired_below=max(1e-6,desired_height-head); sy=desired_below/below
    cx=mid(j['hip_l'],j['hip_r'])[0]
    width_scale=float(model.get('chibiRetarget',{}).get('horizontalScale',1.08))
    outj={}
    for k,(x,y) in j.items():
        ny=y if y <= j['chin'][1] else j['chin'][1]+(y-j['chin'][1])*sy
        nx=cx+(x-cx)*width_scale
        outj[k]=[nx,ny]
    out={'schemaVersion':1,'sourcePose':args.pose,'referenceModel':args.model,'sourceHeadCount':current_heads,
      'targetHeadCount':args.target_head_count,'verticalBodyScaleBelowChin':sy,'horizontalScale':width_scale,'joints':outj,
      'preserve':['joint topology','left/right identity','pose intent','instrument contact target'],
      'appearanceConstraints':model.get('appearanceConstraints',{}),'renderConstraints':model.get('renderConstraints',{})}
    Path(args.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__': main()
