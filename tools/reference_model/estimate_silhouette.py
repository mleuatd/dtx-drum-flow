#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import cv2,numpy as np

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--image',required=True); ap.add_argument('--output',required=True)
    ap.add_argument('--debug')
    a=ap.parse_args()
    img=cv2.imread(a.image); h,w=img.shape[:2]
    mask=np.zeros((h,w),np.uint8); bg=np.zeros((1,65),np.float64); fg=np.zeros((1,65),np.float64)
    rect=(max(1,int(w*.08)),max(1,int(h*.025)),max(2,int(w*.84)),max(2,int(h*.95)))
    cv2.grabCut(img,mask,rect,bg,fg,5,cv2.GC_INIT_WITH_RECT)
    fgmask=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),1,0).astype(np.uint8)
    num,lab,stats,_=cv2.connectedComponentsWithStats(fgmask,8)
    if num<=1: raise SystemExit('silhouette extraction failed')
    idx=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]); comp=(lab==idx).astype(np.uint8)
    x,y,bw,bh,area=stats[idx].tolist()
    data={'schemaVersion':1,'provider':'opencv-grabcut','image':a.image,'imageSize':[w,h],
      'bboxRaw':[x,y,x+bw,y+bh],'bboxNormalized':[x/w,y/h,(x+bw)/w,(y+bh)/h],'areaPixels':area,'status':'PROVISIONAL_NEEDS_VISUAL_REVIEW'}
    Path(a.output).write_text(json.dumps(data,indent=2)+'\n')
    if a.debug:
        overlay=img.copy(); overlay[comp==0]=(overlay[comp==0]*0.25).astype(np.uint8); cv2.rectangle(overlay,(x,y),(x+bw,y+bh),(0,255,0),2); cv2.imwrite(a.debug,overlay)
    print(json.dumps(data))
if __name__=='__main__':main()
