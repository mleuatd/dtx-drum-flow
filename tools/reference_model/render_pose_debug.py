#!/usr/bin/env python3
import argparse,json,cv2
from pathlib import Path
EDGES=[('head_top','chin'),('shoulder_l','shoulder_r'),('shoulder_l','elbow_l'),('elbow_l','wrist_l'),('shoulder_r','elbow_r'),('elbow_r','wrist_r'),('shoulder_l','hip_l'),('shoulder_r','hip_r'),('hip_l','hip_r'),('hip_l','knee_l'),('knee_l','ankle_l'),('hip_r','knee_r'),('knee_r','ankle_r')]
def pt(x): return tuple(int(round(v)) for v in x) if isinstance(x,list) and len(x)==2 else None
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--image',required=True); ap.add_argument('--landmarks',required=True); ap.add_argument('--view-index',type=int,required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    img=cv2.imread(a.image); d=json.loads(Path(a.landmarks).read_text()); v=next(x for x in d['views'] if x['index']==a.view_index); p=v['pose']
    for x,y in EDGES:
        a1=pt(p.get(x)); b1=pt(p.get(y))
        if a1 and b1: cv2.line(img,a1,b1,(0,255,255),2)
    groups=[('pose',(0,255,0)),('hair',(255,0,255)),('garment',(255,255,0)),('footwear',(0,128,255))]
    for name,col in groups:
        for k,val in v.get(name,{}).items():
            q=pt(val)
            if q: cv2.circle(img,q,5,col,-1); cv2.putText(img,k,q,cv2.FONT_HERSHEY_SIMPLEX,.35,col,1,cv2.LINE_AA)
    cv2.imwrite(a.output,img); print(a.output)
if __name__=='__main__':main()
