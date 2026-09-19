#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize, remove_small_objects

TOOL_VERSION='1.0.0'
def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def load_profile(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def hatch_mask(tone, angle_deg, spacing, threshold):
    h,w=tone.shape; yy,xx=np.mgrid[:h,:w]; th=np.deg2rad(angle_deg)
    coord=xx*np.cos(th)+yy*np.sin(th)
    return (np.mod(np.floor(coord),spacing)==0) & (tone>=threshold)
def main():
    ap=argparse.ArgumentParser(description='Deterministic raster image -> pencil dessin linework; no solid fill.')
    ap.add_argument('--input',required=True); ap.add_argument('--output',required=True); ap.add_argument('--profile',required=True); ap.add_argument('--qa-report')
    a=ap.parse_args(); p=load_profile(a.profile)
    src=cv2.imread(a.input,cv2.IMREAD_COLOR)
    if src is None: raise SystemExit('cannot read input')
    gray=cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
    smooth=cv2.bilateralFilter(gray,int(p['bilateralDiameter']),float(p['bilateralSigmaColor']),float(p['bilateralSigmaSpace']))
    can=cv2.Canny(smooth,int(p['cannyLow']),int(p['cannyHigh']),L2gradient=True)>0
    lap=np.abs(cv2.Laplacian(smooth,cv2.CV_32F,ksize=3)); detail=lap>=float(p['detailLaplacianThreshold'])
    edges=remove_small_objects(can|detail,min_size=int(p['minimumComponentPixels']))
    sk=skeletonize(edges)
    h,w=gray.shape; darkness=np.zeros((h,w),np.float32)
    for dx,dy,alpha in p['retracePasses']:
        shifted=ndimage.shift(sk.astype(np.uint8),shift=(int(dy),int(dx)),order=0,mode='constant',cval=0)>0
        darkness=1-(1-darkness)*(1-shifted.astype(np.float32)*float(alpha))
    tone=1.0-smooth.astype(np.float32)/255.0
    border=np.concatenate([gray[0,:],gray[-1,:],gray[:,0],gray[:,-1]])
    bg=float(np.median(border))
    if float(np.std(border)) <= float(p.get('uniformBackgroundStdMax',18)):
        foreground=np.abs(gray.astype(np.float32)-bg)>float(p.get('uniformBackgroundTolerance',12))
        foreground=ndimage.binary_dilation(foreground,iterations=2); tone=np.where(foreground,tone,0)
    tone=np.where(tone>=float(p['toneFloor']),tone,0)
    hatch=np.zeros_like(darkness)
    for layer in p['hatching']:
        hm=skeletonize(hatch_mask(tone,float(layer['angleDeg']),int(layer['spacingPx']),float(layer['toneThreshold'])))
        hatch=1-(1-hatch)*(1-hm.astype(np.float32)*float(layer['alpha']))
    darkness=1-(1-darkness)*(1-hatch)
    out=np.full((h,w,4),255,np.uint8); graphite=np.array(p.get('graphiteRgb',[30,30,30]),np.float32)
    d=np.clip(darkness,0,1)[...,None]; out[...,:3]=np.clip(255*(1-d)+graphite*d,0,255).astype(np.uint8); out[...,3]=255
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Image.fromarray(out,'RGBA').save(a.output,'PNG',optimize=False)
    report={'schemaVersion':1,'tool':'tools/line_style/image_to_dessin.py','toolVersion':TOOL_VERSION,'profileId':p['profileId'],'sourceSha256':sha256_file(a.input),'outputSha256':sha256_file(a.output),'canvas':[w,h],'edgePixels':int(sk.sum()),'hatchPixels':int((hatch>0).sum()),'noSolidFill':True,'deterministic':True}
    if a.qa_report: Path(a.qa_report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__': main()
