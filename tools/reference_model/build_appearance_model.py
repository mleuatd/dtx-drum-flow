#!/usr/bin/env python3
import argparse,json,math,statistics
from pathlib import Path

def d(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
def valid(p): return isinstance(p,list) and len(p)==2
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--landmarks',required=True); ap.add_argument('--base-profile',required=True); ap.add_argument('--output',required=True)
    a=ap.parse_args(); lm=json.loads(Path(a.landmarks).read_text()); base=json.loads(Path(a.base_profile).read_text())
    ratios={'shoulderWidthHeads':[],'hipWidthHeads':[],'hairWidthHeads':[],'hairLengthHeads':[],'jacketLengthHeads':[],'skirtLengthHeads':[]}
    used=[]
    for v in lm['views']:
        p=v.get('pose',{}); h=v.get('hair',{}); g=v.get('garment',{})
        if not(valid(p.get('head_top')) and valid(p.get('chin'))): continue
        hu=d(p['head_top'],p['chin'])
        if hu<=0: continue
        used.append(v['index'])
        if valid(p.get('shoulder_l')) and valid(p.get('shoulder_r')): ratios['shoulderWidthHeads'].append(d(p['shoulder_l'],p['shoulder_r'])/hu)
        if valid(p.get('hip_l')) and valid(p.get('hip_r')): ratios['hipWidthHeads'].append(d(p['hip_l'],p['hip_r'])/hu)
        if valid(h.get('hair_left_extent')) and valid(h.get('hair_right_extent')): ratios['hairWidthHeads'].append(d(h['hair_left_extent'],h['hair_right_extent'])/hu)
        if valid(h.get('crown')) and valid(h.get('hair_tip_center')): ratios['hairLengthHeads'].append(d(h['crown'],h['hair_tip_center'])/hu)
        if valid(g.get('jacket_shoulder_l')) and valid(g.get('jacket_hem_l')): ratios['jacketLengthHeads'].append(d(g['jacket_shoulder_l'],g['jacket_hem_l'])/hu)
        if valid(g.get('skirt_hem_l')) and valid(p.get('hip_l')): ratios['skirtLengthHeads'].append(d(p['hip_l'],g['skirt_hem_l'])/hu)
    summary={k:(statistics.median(v) if v else None) for k,v in ratios.items()}
    out={'schemaVersion':1,'profileId':'luna_video_appearance_v1','status':'PROVISIONAL_OBSERVED',
      'sourceVideo':base['referenceVideo'],'usedViewIndices':used,'appearanceConstraints':base['appearanceConstraints'],
      'numericRatiosMedian':summary,'numericRatiosByView':ratios,'cameraPolicy':base['cameraPolicy'],'chibiRetarget':base['chibiRetarget'],
      'renderConstraints':base['renderConstraints'],'forbiddenChanges':base['forbiddenChanges']}
    Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
