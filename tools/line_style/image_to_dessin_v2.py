import argparse,json,hashlib,math
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize,remove_small_objects

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prof(p):
 d=json.loads(Path(p).read_text()); assert d['baseStrokeWidth']==1 and d['noSolidFill']; return d
def shift(m,dx,dy):
 o=np.zeros_like(m);h,w=m.shape;sx0=max(0,-dx);sx1=min(w,w-dx);sy0=max(0,-dy);sy1=min(h,h-dy);dx0=sx0+dx;dy0=sy0+dy
 if sx1>sx0 and sy1>sy0:o[dy0:dy0+sy1-sy0,dx0:dx0+sx1-sx0]=m[sy0:sy1,sx0:sx1]
 return o
def hatch(tone,ang,spacing,phase=0):
 h,w=tone.shape;y,x=np.mgrid[:h,:w];a=np.deg2rad(ang);c=x*np.cos(a)+y*np.sin(a)+phase
 return np.mod(np.floor(c),spacing)==0
def main():
 a=argparse.ArgumentParser();a.add_argument('--input',required=True);a.add_argument('--output',required=True);a.add_argument('--profile',required=True);a.add_argument('--qa-report',required=True);z=a.parse_args();p=prof(z.profile)
 bgr=cv2.imread(z.input); gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY);h,w=gray.shape
 sm=cv2.bilateralFilter(gray,5,24,24);lo=max(8,int(115-p['edgeSensitivity']*75));hi=max(lo+20,int(220-p['edgeSensitivity']*100))
 edge=cv2.Canny(sm,lo,hi,L2gradient=True)>0;lap=np.abs(cv2.Laplacian(sm,cv2.CV_32F,ksize=3));detail=lap>max(8,48-p['detailSensitivity']*30)
 src=remove_small_objects(edge|detail,min_size=3);sk=skeletonize(src)
 tone=1-gray.astype(np.float32)/255.
 border=np.concatenate([gray[0],gray[-1],gray[:,0],gray[:,-1]]);bg=float(np.median(border))
 if float(np.std(border))<18:
  fg=np.abs(gray.astype(np.float32)-bg)>18;fg=ndimage.binary_closing(fg,iterations=5);fg=ndimage.binary_fill_holes(fg);fg=ndimage.binary_dilation(fg,iterations=2);tone=np.where(fg,tone,0)
 local=ndimage.maximum_filter(tone,size=5);ink=np.zeros((h,w),np.float32);rng=np.random.default_rng(int(p['deterministicSeed']))
 maxn=int(p['strokeCountMax']);minn=int(p['strokeCountMin']);spread=float(p['retraceSpreadPx']);rough=float(p['roughness'])
 countmap=np.clip(np.rint(minn+(maxn-minn)*np.power(local,float(p['toneToStrokeCount']))),minn,maxn).astype(np.int16)
 for i in range(maxn):
  dx=int(np.clip(np.rint(rng.normal(0,spread*(.25+.75*rough))),-max(1,math.ceil(spread)),max(1,math.ceil(spread))))
  dy=int(np.clip(np.rint(rng.normal(0,spread*(.25+.75*rough))),-max(1,math.ceil(spread)),max(1,math.ceil(spread))))
  active=sk&(countmap>i)
  if rough>0 and i>1:
   gate=rng.random((h,w));gate=ndimage.maximum_filter(gate,size=max(2,int(3+p['strokeLengthVariation']*8)));active&=gate>(.18*rough)
  s=shift(active,dx,dy);ink=np.where(s,1-(1-ink)*(1-.20),ink)
 for j,(ang,cross) in enumerate([(24,False),(-31,True)]):
  dens=p['crossHatchingDensity'] if cross else p['hatchingDensity'];spacing=max(4,int(18-12*dens));threshold=.25+(.18 if cross else 0)
  hm=skeletonize(hatch(tone,ang,spacing,j*3)&(tone>threshold));ink=np.where(hm,1-(1-ink)*(1-.14),ink)
 for _ in range(int(p['strayStrokeAmount']*20)):
  s=shift(sk,int(rng.integers(-2,3)),int(rng.integers(-2,3)))&(rng.random((h,w))>.93);ink=np.where(s,1-(1-ink)*(1-.12),ink)
 out=np.clip(255-ink*220,0,255).astype(np.uint8);Image.fromarray(out,'L').save(z.output)
 out_edges=out<245;dil=ndimage.binary_dilation(sk,iterations=3);solid=ndimage.binary_erosion(out<80,iterations=2)
 q={'schemaVersion':2,'tool':'image_to_dessin_v2.py','profileId':p['profileId'],'inputSha256':sha(z.input),'outputSha256':sha(z.output),'baseStrokeWidth':1,'noSolidFill':True,'roughness':rough,'configuredStrokeCount':[minn,maxn],'renderedStrokePasses':maxn,'hatchingDensity':p['hatchingDensity'],'crossHatchingDensity':p['crossHatchingDensity'],'thinLineDensity':float(out_edges.sum()/(h*w)),'edgeMatchRatio':float((out_edges&dil).sum()/max(1,out_edges.sum())),'silhouetteRetentionProxy':float((out_edges&ndimage.binary_dilation(sk,iterations=1)).sum()/max(1,sk.sum())),'solidFillRatio':float(solid.sum()/(h*w)),'deterministicSeed':p['deterministicSeed']}
 Path(z.qa_report).write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\\n');print(json.dumps(q,ensure_ascii=False))
if __name__=='__main__':main()
