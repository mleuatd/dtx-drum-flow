#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def cubic(p0,p1,p2,p3,t):
    u=1.0-t
    return (
        u*u*u*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t*t*t*p3[0],
        u*u*u*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t*t*t*p3[1],
    )

def load_profile(path):
    p=json.loads(Path(path).read_text(encoding='utf-8'))
    if p.get('schemaVersion')!=1:
        raise ValueError('unsupported profile schemaVersion')
    strands=p.get('strands') or []
    required=(p.get('topologyRules') or {}).get('requiredStrandCount',2)
    if len(strands)!=required:
        raise ValueError(f'profile requires exactly {required} strands')
    for s in strands:
        bz=s.get('bezier')
        if not isinstance(bz,list) or len(bz)!=4 or any(len(q)!=2 for q in bz):
            raise ValueError(f'invalid bezier for {s.get("id")}')
    return p

def main():
    ap=argparse.ArgumentParser(description='Deterministically add locked cowlick strokes inside a crown ROI.')
    ap.add_argument('--input',required=True)
    ap.add_argument('--profile',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--qa-report',required=True)
    ap.add_argument('--expected-source-sha256')
    ap.add_argument('--overwrite',action='store_true')
    args=ap.parse_args()

    src_path=Path(args.input); out_path=Path(args.output); qa_path=Path(args.qa_report)
    if src_path.resolve()==out_path.resolve():
        raise SystemExit('REFUSE: output must not overwrite source')
    if out_path.exists() and not args.overwrite:
        raise SystemExit('REFUSE: output exists; use --overwrite for candidate files only')

    profile=load_profile(args.profile)
    source_sha=sha256_file(src_path)
    if args.expected_source_sha256 and source_sha.lower()!=args.expected_source_sha256.lower():
        raise SystemExit(f'REFUSE: source SHA mismatch: {source_sha}')

    src=Image.open(src_path).convert('RGBA')
    cw,ch=profile['canvas']['width'],profile['canvas']['height']
    if src.size!=(cw,ch):
        raise SystemExit(f'REFUSE: canvas mismatch {src.size} != {(cw,ch)}')

    roi=profile['roi']; x0,y0,w,h=[int(roi[k]) for k in ('x','y','width','height')]
    if x0<0 or y0<0 or x0+w>cw or y0+h>ch:
        raise SystemExit('REFUSE: ROI outside canvas')

    overlay=Image.new('RGBA',src.size,(0,0,0,0))
    draw=ImageDraw.Draw(overlay)
    render=profile['render']; samples=max(8,int(render.get('samplesPerBezier',72)))
    rgba0=tuple(render.get('rgba',[18,18,18,220])); width=max(1,int(render.get('baseWidth',2)))

    for strand in profile['strands']:
        bp=[(x0+float(nx)*w,y0+float(ny)*h) for nx,ny in strand['bezier']]
        pts=[cubic(*bp,i/samples) for i in range(samples+1)]
        for ps in render.get('passes',[{'dx':0,'dy':0,'alphaScale':1.0}]):
            dx=float(ps.get('dx',0)); dy=float(ps.get('dy',0)); scale=float(ps.get('alphaScale',1.0))
            rgba=(rgba0[0],rgba0[1],rgba0[2],max(0,min(255,round(rgba0[3]*scale))))
            draw.line([(round(x+dx),round(y+dy)) for x,y in pts],fill=rgba,width=width,joint='curve')

    clipped=Image.new('RGBA',src.size,(0,0,0,0))
    clipped.alpha_composite(overlay.crop((x0,y0,x0+w,y0+h)),dest=(x0,y0))
    out=Image.alpha_composite(src.copy(),clipped)

    a=src.load(); b=out.load(); outside=inside=0
    for y in range(ch):
        in_y=y0<=y<y0+h
        for x in range(cw):
            if a[x,y]!=b[x,y]:
                if in_y and x0<=x<x0+w: inside+=1
                else: outside+=1
    if outside!=0:
        raise SystemExit(f'REFUSE: outside ROI changed pixels = {outside}')

    out_path.parent.mkdir(parents=True,exist_ok=True)
    qa_path.parent.mkdir(parents=True,exist_ok=True)
    out.save(out_path,format='PNG',optimize=False)
    report={
        'schemaVersion':1,'tool':'tools/cowlick/apply_cowlick.py',
        'profileId':profile['profileId'],'sourcePath':str(src_path),
        'sourceSha256':source_sha,'outputPath':str(out_path),
        'outputSha256':sha256_file(out_path),'canvas':[cw,ch],'roi':roi,
        'insideRoiChangedPixels':inside,'outsideRoiChangedPixels':outside,
        'pass':outside==0 and inside>0
    }
    qa_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    if not report['pass']:
        raise SystemExit('REFUSE: no meaningful ROI change or QA failed')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
    main()
