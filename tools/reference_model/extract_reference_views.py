#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import cv2

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--video',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--views',type=int,default=12)
    ap.add_argument('--manifest',required=True)
    args=ap.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    cap=cv2.VideoCapture(args.video)
    if not cap.isOpened(): raise SystemExit('cannot open video')
    fps=float(cap.get(cv2.CAP_PROP_FPS)); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if n < 2 or fps <= 0: raise SystemExit('invalid video metadata')
    entries=[]
    for i in range(args.views):
        idx=round(i*(n-1)/(args.views-1)) if args.views>1 else 0
        yaw=round(i*360.0/(args.views-1),3) if args.views>1 else 0.0
        cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ok,frame=cap.read()
        if not ok: raise SystemExit(f'failed frame {idx}')
        fn=f'view_{i:02d}_yaw_{int(round(yaw)):03d}.png'; fp=out/fn
        cv2.imwrite(str(fp),frame)
        entries.append({'index':i,'frameIndex':idx,'timeSec':idx/fps,'yawDeg':yaw,'path':str(fp),'sha256':sha256_file(fp)})
    cap.release()
    manifest={'schemaVersion':1,'type':'multiview_reference_video','videoPath':args.video,'videoSha256':sha256_file(args.video),
      'videoBytes':Path(args.video).stat().st_size,'width':w,'height':h,'fps':fps,'frameCount':n,'durationSec':n/fps,
      'yawConvention':'view sequence mapped monotonically 0..360; calibration may refine offset/direction','views':entries}
    Path(args.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__': main()
