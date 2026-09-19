#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from common import *

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True); ap.add_argument('--profile',required=True)
    ap.add_argument('--output',required=True); ap.add_argument('--qa-report',required=True)
    ap.add_argument('--expected-source-sha256'); ap.add_argument('--overwrite',action='store_true')
    args=ap.parse_args()
    src=Path(args.input); outp=Path(args.output); qap=Path(args.qa_report)
    if src.resolve()==outp.resolve(): raise SystemExit('REFUSE: source overwrite forbidden')
    if outp.exists() and not args.overwrite: raise SystemExit('REFUSE: output exists')
    p=load_profile(args.profile); sha=sha256_file(src)
    if args.expected_source_sha256 and sha.lower()!=args.expected_source_sha256.lower(): raise SystemExit('REFUSE: source SHA mismatch')
    rgba=rgba_array(src); h,w=rgba.shape[:2]
    c=p['canvas']; expected=(int(c['width']),int(c['height']))
    if (w,h)!=expected: raise SystemExit('REFUSE: canvas mismatch')
    mask,dark=ink_mask(rgba,p); sk,_=skeleton_and_distance(mask)
    local=ndimage.maximum_filter(dark,size=3,mode='nearest')
    result_dark=np.clip(dark*float(p['lineExtraction']['preserveOriginalWeight']),0,1)
    thresholds=p['densityThresholds']
    for i,((dx,dy),pa) in enumerate(zip(p['passOffsets'],p['passAlpha'])):
        if i==0: active=sk
        elif i==1: active=sk & (local>=float(thresholds['pass2']))
        elif i==2: active=sk & (local>=float(thresholds['pass3']))
        else: active=sk & (local>=float(thresholds['pass4']))
        shifted=shift_bool(active,int(dx),int(dy)); a=float(pa)
        result_dark=np.where(shifted,1.0-(1.0-result_dark)*(1.0-a),result_dark)
    allowed=ndimage.binary_dilation(mask,iterations=1)
    result_dark=np.where(allowed,result_dark,dark)
    normalized=compose_black_on_transparency_from_darkness(rgba,result_dark)
    empty=(rgba[...,3]==0)&(~allowed); normalized[empty]=rgba[empty]
    outp.parent.mkdir(parents=True,exist_ok=True); qap.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(normalized,'RGBA').save(outp,format='PNG',optimize=False)
    changed=np.any(normalized!=rgba,axis=2)
    report={'schemaVersion':1,'toolVersion':TOOL_VERSION,'tool':'tools/line_style/normalize_line_style.py','profileId':p['profileId'],
      'sourcePath':str(src),'sourceSha256':sha,'outputPath':str(outp),'outputSha256':sha256_file(outp),'canvas':[w,h],
      'changedPixels':int(changed.sum()),'changedBbox':bbox_from_mask(changed),'sourceInkPixels':int(mask.sum()),
      'sourceSkeletonPixels':int(sk.sum()),'baseLineWidthPx':p['baseLineWidthPx'],'strokePassesConfigured':len(p['passOffsets']),
      'renderMode':p['render']['retraceMode'],'formalPromoted':False}
    qap.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__': main()
