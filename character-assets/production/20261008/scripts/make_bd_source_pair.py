from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import map_coordinates
repo=next(p for p in Path(__file__).resolve().parents if (p/'character-assets').is_dir()); root=repo.parent; W,H=1448,1086
n=Image.open(root/'work_output/sources/neutral.png').convert('RGBA');na=np.array(n)
b=Image.open(repo/'character-assets/production/20261008/donors/right_boot_rear_candidate.png').convert('RGBA').resize((260,350),Image.Resampling.LANCZOS)
ba=np.array(b);gray=np.mean(ba[:,:,:3],axis=2).astype('uint8');ba[:,:,:3]=gray[:,:,None];b=Image.fromarray(ba)
src=np.array([[128,110,1],[184,191,1],[122,310,1]],float);dst=np.array([[674,830],[719,891],[663,974]],float);A=np.linalg.solve(src,dst).T;M=np.vstack([A,[0,0,1]]);inv=np.linalg.inv(M)
boot=b.transform((W,H),Image.Transform.AFFINE,tuple(inv[:2].ravel()),Image.Resampling.BICUBIC);bo=np.array(boot);bo[:817]=0;boot=Image.fromarray(bo)
def poly(points):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
base=na.copy(); clear=poly([(640,730),(713,730),(735,847),(753,946),(637,955),(577,913),(587,866),(624,822),(634,769)]);base[clear]=0
for x0,y0,x1,y1 in [(712,742,743,804),(723,804,750,834),(733,834,761,879)]:base[y0:y1,x0:x1]=na[y0:y1,x0:x1]
yy,xx=np.mgrid[:H,:W];oldy=730+(yy-730)*70/101;w=np.clip((oldy-730)/70,0,1);oldx=(xx-(682-8*w))/(1-.2*w)+682
sm=poly([(640,729),(710,729),(711,798),(682,806),(651,800)]);skin0=na.copy();skin0[~sm]=0
skin=np.stack([map_coordinates(skin0[:,:,k],[oldy,oldx],order=1,mode='constant',cval=0) for k in range(4)],axis=2).astype('uint8');skin[:730]=0
leg=Image.alpha_composite(Image.fromarray(skin),boot)
l=np.array(leg);ry=yy+12*np.clip((yy-730)/70,0,1);rl=np.stack([map_coordinates(l[:,:,k],[ry,xx],order=1,mode='constant',cval=0) for k in range(4)],axis=2).astype('uint8')
out=root/'work_output/variants/bd';out.mkdir(parents=True,exist_ok=True)
kit=Image.open(root/'work_output/sources/drum_fixed.png').convert('RGBA')
for ph,ll in [('hit',leg),('rebound',Image.fromarray(rl))]:
 im=Image.alpha_composite(Image.fromarray(base),ll);im.save(out/f'{ph}_rf_source_candidate.png');preview=Image.alpha_composite(Image.new('RGBA',(W,H),'white'),kit);preview=Image.alpha_composite(preview,im);preview.save(root/f'work_output/previews/bd_{ph}_candidate.png');preview.crop((560,700,800,1030)).resize((480,660)).save(root/f'work_output/qa/bd_{ph}_detail.png')
print('Candidate only: visible anatomy/contact QA required before promotion.')
