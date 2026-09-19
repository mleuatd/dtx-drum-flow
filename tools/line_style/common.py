from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

TOOL_VERSION = "1.0.0"

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def load_profile(path):
    p=json.loads(Path(path).read_text(encoding='utf-8'))
    if p.get('schemaVersion') != 1: raise ValueError('unsupported schemaVersion')
    if int(p.get('baseLineWidthPx',0)) != 1: raise ValueError('baseLineWidthPx must be exactly 1')
    offs=p.get('passOffsets') or []; alphas=p.get('passAlpha') or []
    if not offs or len(offs)!=len(alphas): raise ValueError('passOffsets/passAlpha mismatch')
    if p.get('noThickBrush') is not True or p.get('noSolidFill') is not True: raise ValueError('safety flags must be true')
    return p

def rgba_array(path): return np.array(Image.open(path).convert('RGBA'),dtype=np.uint8)

def visual_darkness(rgba):
    rgb=rgba[...,:3].astype(np.float32)/255.0
    a=rgba[...,3:4].astype(np.float32)/255.0
    comp=rgb*a+(1.0-a)
    lum=0.2126*comp[...,0]+0.7152*comp[...,1]+0.0722*comp[...,2]
    return np.clip(1.0-lum,0.0,1.0)

def ink_mask(rgba, profile):
    d=visual_darkness(rgba)
    mask=d>=float(profile['lineExtraction']['visualDarknessThreshold'])
    minc=int(profile['lineExtraction'].get('minimumComponentPixels',2))
    if minc>1:
        lab,n=ndimage.label(mask)
        if n:
            sizes=np.bincount(lab.ravel()); keep=sizes>=minc; keep[0]=False; mask=keep[lab]
    return mask,d

def skeleton_and_distance(mask):
    sk=skeletonize(mask)
    return sk,ndimage.distance_transform_edt(~sk)

def bbox_from_mask(mask):
    ys,xs=np.where(mask)
    if len(xs)==0:return None
    return [int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]

def shift_bool(mask,dx,dy):
    out=np.zeros_like(mask); h,w=mask.shape
    sx0=max(0,-dx); sx1=min(w,w-dx); sy0=max(0,-dy); sy1=min(h,h-dy)
    dx0=sx0+dx; dx1=sx1+dx; dy0=sy0+dy; dy1=sy1+dy
    if sx1>sx0 and sy1>sy0: out[dy0:dy1,dx0:dx1]=mask[sy0:sy1,sx0:sx1]
    return out

def compose_black_on_transparency_from_darkness(source_rgba,darkness):
    a=np.clip(darkness*255.0,0,255).astype(np.uint8)
    out=np.empty_like(source_rgba); out[...,:3]=20; out[...,3]=a
    return out
