#!/usr/bin/env python3
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def fit(im, size=(480,360)):
    c=Image.new('RGBA', size, (255,255,255,255))
    x=im.convert('RGBA').copy()
    x.thumbnail(size)
    c.alpha_composite(x, ((size[0]-x.width)//2,(size[1]-x.height)//2))
    return c.convert('RGB')

def changed(a,b):
    d=ImageChops.difference(a.convert('RGBA'),b.convert('RGBA'))
    m=Image.new('L',a.size,0)
    for band in d.split(): m=ImageChops.lighter(m,band)
    return sum(1 for v in m.getdata() if v)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--request',required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    req=json.loads(Path(args.request).read_text(encoding='utf-8'))
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    allpaths={}
    for group in ('formal','parents','donors'):
        for name,path in req.get(group,{}).items():
            allpaths[f'{group}__{name}']=Path(path)
    report={'request':req,'files':{},'pairs':{},'machineQa':'PASS'}
    thumbs=[]
    for key,p in allpaths.items():
        if not p.exists():
            report['machineQa']='FAIL'
            report.setdefault('missing',[]).append(str(p)); continue
        dst=out/(key+p.suffix.lower())
        shutil.copy2(p,dst)
        report['files'][key]={'path':str(p),'sha256':sha256(p),'bytes':p.stat().st_size}
        try:
            im=Image.open(p)
            report['files'][key]['size']=list(im.size)
            thumbs.append((key,fit(im)))
        except Exception:
            pass
    if report['machineQa']=='FAIL':
        (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        raise SystemExit('missing requested sources')
    # compact evidence sheet, plus useful measured pair deltas
    cols=3; cellw,cellh=480,400
    rows=(len(thumbs)+cols-1)//cols
    sheet=Image.new('RGB',(cols*cellw,rows*cellh),'white')
    dr=ImageDraw.Draw(sheet)
    for i,(name,im) in enumerate(thumbs):
        x=(i%cols)*cellw; y=(i//cols)*cellh
        sheet.paste(im,(x,y)); dr.text((x+8,y+365),name,fill='black')
    sheet.save(out/'source_sheet.jpg',quality=92)
    for phase in ('hit','rebound'):
        fk=f'formal__{phase}'; pk=f'parents__{phase}'
        if fk in report['files'] and pk in report['files']:
            a=Image.open(allpaths[fk]); b=Image.open(allpaths[pk])
            report['pairs'][f'formal_to_parent_{phase}']={'changedPixels':changed(a,b)}
        dk=f'donors__bd_{phase}'
        rk=f'donors__rc_{phase}'
        if dk in report['files'] and rk in report['files']:
            a=Image.open(allpaths[dk]); b=Image.open(allpaths[rk])
            report['pairs'][f'bd_to_rc_{phase}']={'changedPixels':changed(a,b)}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
