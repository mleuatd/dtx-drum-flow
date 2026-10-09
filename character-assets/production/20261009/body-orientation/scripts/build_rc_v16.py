from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path(__file__).resolve().parents[5];O=R/'character-assets/production/20261009/body-orientation'
b=np.array(Image.open(R/'character-assets/layers/character/rc/hit_r_refresh.png').convert('RGBA'));d=np.array(Image.open(O/'candidates/rc_hit_registered_v3.png').convert('RGBA'));a=b.copy();a[:530]=d[:530];a[:450,1100:]=b[:450,1100:]
# Join individual pencil strand bundles inside the hair, above protected y590.
mask=Image.new('L',(1448,1086));ImageDraw.Draw(mask).polygon([(700,530),(1002,530),(969,589),(700,589)],fill=255);m=np.array(mask)>0; a[m]=(255,255,255,255)
im=Image.fromarray(a);draw=ImageDraw.Draw(im)
def bundles(src,y):
 gray=src[y,:,:3].mean(1);dark=np.where((gray[700:1002]<140)&(src[y,700:1002,3]>200))[0]+700
 runs=np.split(dark,np.where(np.diff(dark)>3)[0]+1)
 return [(float(x.mean()),min(5,max(1,len(x)//2))) for x in runs if len(x)>1]
top=bundles(d,529);bottom=bundles(b,590)
for i,(x,width) in enumerate(top):
 dest=min(bottom,key=lambda t:abs(t[0]-x))[0];pts=[]
 for y in range(529,591):
  t=(y-529)/61;xx=x+(dest-x)*(t*t*(3-2*t));pts.append((xx,y))
 draw.line(pts,fill=(65,65,65,255),width=width)
 draw.line([(x-1,y) for x,y in pts],fill=(140,140,140,220),width=1)
for x,width in bottom:
 if min(abs(x-v[0]) for v in top)>8:
  start=min(top,key=lambda t:abs(t[0]-x))[0];draw.line([(start,540),(x,575),(x,590)],fill=(80,80,80,255),width=width)
a=np.array(im);a[590:]=b[590:];Image.fromarray(a).save(O/'candidates/rc_hit_v16.png')
dr=Image.open(R/'character-assets/layers/drum/drum_base.png').convert('RGBA');bg=Image.new('RGBA',dr.size,'white');bg.alpha_composite(dr);bg.alpha_composite(Image.fromarray(a));bg.convert('RGB').save(O/'qa/rc_hit_composite_v16.png')
(O/'qa/rc_v16_mechanical.json').write_text(json.dumps({'status':'REJECTED','reason':'Artificial white band with straight bridging strokes changes pencil texture; cuff/left sleeve connection remains cut.','lower_y590_equal':bool(np.array_equal(a[590:],b[590:]))},indent=2))

import hashlib
p=O/'qa/resume_attempt_20261009.json';report=json.loads(p.read_text())
report['trials']=[e for e in report['trials'] if e['version']!=16]+[{'version':16,'phase':'hit','file':str((O/'candidates/rc_hit_v16.png').relative_to(R)),'sha256':hashlib.sha256((O/'candidates/rc_hit_v16.png').read_bytes()).hexdigest(),'status':'REJECTED','visualReview':'Direct full image inspection','reason':'Artificial white band with straight bridging strokes changes pencil texture; cuff/left sleeve connection remains cut.'}]
p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
