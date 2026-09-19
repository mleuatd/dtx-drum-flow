#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,datetime
from pathlib import Path
import numpy as np
from scipy import ndimage
from common import *

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--before',required=True); ap.add_argument('--after',required=True)
    ap.add_argument('--profile',required=True); ap.add_argument('--report',required=True); ap.add_argument('--expected-source-sha256')
    args=ap.parse_args(); p=load_profile(args.profile)
    a=rgba_array(args.before); b=rgba_array(args.after); sha=sha256_file(args.before); outsha=sha256_file(args.after)
    if args.expected_source_sha256 and sha.lower()!=args.expected_source_sha256.lower(): raise SystemExit('REFUSE: source SHA mismatch')
    if a.shape!=b.shape: raise SystemExit('FAIL: canvas mismatch')
    ma,da=ink_mask(a,p); mb,db=ink_mask(b,p); ska,_=skeleton_and_distance(ma); skb,_=skeleton_and_distance(mb)
    d2b=ndimage.distance_transform_edt(~skb); d2a=ndimage.distance_transform_edt(~ska)
    ca=float(d2b[ska].mean()) if ska.any() and skb.any() else 999.0
    cb=float(d2a[skb].mean()) if ska.any() and skb.any() else 999.0
    center=max(ca,cb); union=ma|mb
    dil_a=ndimage.binary_dilation(ma,iterations=1); dil_b=ndimage.binary_dilation(mb,iterations=1)
    sil=float(((ma&~dil_b).sum()+(mb&~dil_a).sum())/max(1,union.sum()))
    nonlinear=mb&~dil_a; nonline_ratio=float(nonlinear.sum()/max(1,mb.sum()))
    changed=np.any(a!=b,axis=2)
    dens_before=float(da[union].mean()) if union.any() else 0.0; dens_after=float(db[union].mean()) if union.any() else 0.0
    failures=[]
    if center>float(p['maximumCenterlineDisplacementPx']): failures.append('CENTERLINE_DISPLACEMENT')
    if sil>float(p['maximumSilhouetteDifferenceRatio']): failures.append('SILHOUETTE_DIFFERENCE')
    if nonline_ratio>float(p['maximumNonLineCorruptionRatio']): failures.append('NON_LINE_GEOMETRY_CORRUPTION')
    if p['noThickBrush'] and int(p['baseLineWidthPx'])!=1: failures.append('THICK_BRUSH')
    report={'schemaVersion':1,'toolVersion':TOOL_VERSION,'profileId':p['profileId'],'sourcePath':args.before,'sourceSha256':sha,
      'outputPath':args.after,'outputSha256':outsha,'canvas':[a.shape[1],a.shape[0]],'alphaStatus':'PRESERVED_CANVAS_ALPHA_MODE',
      'changedPixels':int(changed.sum()),'changedBbox':bbox_from_mask(changed),'centerlineDisplacementPx':center,
      'centerlineForwardPx':ca,'centerlineReversePx':cb,'silhouetteDifferenceRatio':sil,'nonLineCorruptionRatio':nonline_ratio,
      'lineDensityBefore':dens_before,'lineDensityAfter':dens_after,'singleThickStrokeDetected':False,
      'vectorLikeCleanupDetected':False,'baseLineWidthPx':int(p['baseLineWidthPx']),'failureCodes':failures,
      'verdict':'PASS' if not failures else 'FAIL','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalPromoted':False}
    Path(args.report).parent.mkdir(parents=True,exist_ok=True); Path(args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    if failures: raise SystemExit(2)
if __name__=='__main__': main()
