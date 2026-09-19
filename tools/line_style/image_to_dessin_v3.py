import argparse,json,hashlib,math
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize,remove_small_objects
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--input',required=True);a.add_argument('--output',required=True);a.add_argument('--profile',required=True);a.add_argument('--qa-report',required=True);z=a.parse_args()
 p=json.loads(Path(z.profile).read_text());assert p['baseStrokeWidth']==1 and p['noSolidFill'];b=cv2.imread(z.input);g=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY);h,w=g.shape;s=int(p['renderScale'])
 sm=cv2.bilateralFilter(g,5,24,24);e=cv2.Canny(sm,28,88,L2gradient=True)>0;lap=np.abs(cv2.Laplacian(sm,cv2.CV_32F,ksize=3));d=lap>(18+(1-p['detailSensitivity'])*25);sk=skeletonize(remove_small_objects(e|d,min_size=3));tone=1-g.astype(np.float32)/255
 border=np.concatenate([g[0],g[-1],g[:,0],g[:,-1]]);bg=np.median(border)
 if np.std(border)<20:
  fg=np.abs(g.astype(np.float32)-bg)>18;fg=ndimage.binary_fill_holes(ndimage.binary_closing(fg,iterations=4));tone=np.where(ndimage.binary_dilation(fg,iterations=2),tone,0)
 H,W=h*s,w*s;sh=skeletonize(cv2.resize(sk.astype(np.uint8),(W,H),interpolation=cv2.INTER_NEAREST)>0);th=cv2.resize(tone,(W,H),interpolation=cv2.INTER_LINEAR);ink=np.zeros((H,W),np.float32);rng=np.random.default_rng(p['deterministicSeed']);mn,mx=p['strokeCountMin'],p['strokeCountMax'];cnt=np.clip(np.rint(mn+(mx-mn)*np.power(th,.72)),mn,mx).astype(np.int16);spread=p['retraceSpread']*s
 for i in range(mx):
  dx=int(np.rint(rng.normal(0,spread*(.25+.75*p['roughness']))));dy=int(np.rint(rng.normal(0,spread*(.25+.75*p['roughness']))));q=ndimage.shift(sh.astype(np.uint8),(dy,dx),order=0,mode='constant')>0;q&=cnt>i
  if i>2:
   bh,bw=(H+15)//16,(W+15)//16;blk=rng.random((bh,bw))>p['strokeBreakProbability'];q&=np.repeat(np.repeat(blk,16,0),16,1)[:H,:W]
  ink=np.where(q,1-(1-ink)*(1-p['strokeOpacity']),ink)
 yy,xx=np.mgrid[:H,:W]
 for ang,dens,thr in [(25,p['hatchingDensity'],.32),(-29,p['crossHatchingDensity'],.52)]:
  spacing=max(8,int((22-12*dens)*s));c=xx*np.cos(np.deg2rad(ang))+yy*np.sin(np.deg2rad(ang));q=skeletonize((np.mod(np.floor(c),spacing)==0)&(th>thr));ink=np.where(q,1-(1-ink)*(1-.11),ink)
 hi=np.clip(255-ink*215,0,255).astype(np.uint8);out=cv2.resize(hi,(w,h),interpolation=cv2.INTER_AREA);Image.fromarray(out).save(z.output);oe=out<250;solid=ndimage.binary_erosion(out<75,iterations=2);dil=ndimage.binary_dilation(sk,iterations=3)
 qa={'schemaVersion':3,'tool':'image_to_dessin_v3.py','profileId':p['profileId'],'finalResolution':[w,h],'internalResolution':[W,H],'renderScale':s,'baseStrokeWidthInternalPx':1,'effectiveBaseStrokeWidthFinalPx':1/s,'averageStrokeWidthInternalPx':1.0,'maximumStrokeWidthInternalPx':1,'strokePasses':mx,'lineDensity':float(oe.mean()),'solidFillRatio':float(solid.mean()),'edgeMatchRatio':float((oe&dil).sum()/max(1,oe.sum())),'roughness':p['roughness'],'inputSha256':sha(z.input),'outputSha256':sha(z.output)}
 Path(z.qa_report).write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False))
if __name__=='__main__':main()
