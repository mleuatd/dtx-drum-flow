#!/usr/bin/env python3
import argparse,json
from pathlib import Path
def ispt(x): return isinstance(x,list) and len(x)==2 and all(isinstance(v,(int,float)) for v in x)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--landmarks',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
    d=json.loads(Path(a.landmarks).read_text()); errors=[]; warnings=[]; observed=0
    for v in d.get('views',[]):
        p=v.get('pose',{})
        pts=[x for x in p.values() if ispt(x)]; observed += len(pts)
        for side in ['l','r']:
            sh=p.get('shoulder_'+side); hi=p.get('hip_'+side); an=p.get('ankle_'+side)
            if ispt(sh) and ispt(hi) and sh[1]>=hi[1]: errors.append(f"view{v['index']} shoulder_{side} below/equal hip")
            if ispt(hi) and ispt(an) and hi[1]>=an[1]: errors.append(f"view{v['index']} hip_{side} below/equal ankle")
        if v.get('status')=='NEEDS_OBSERVATION': warnings.append(f"view{v['index']} not observed")
    out={'schemaVersion':1,'observedPosePoints':observed,'errors':errors,'warnings':warnings,'verdict':'PASS' if not errors else 'FAIL'}
    Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
    if errors: raise SystemExit(2)
if __name__=='__main__':main()
