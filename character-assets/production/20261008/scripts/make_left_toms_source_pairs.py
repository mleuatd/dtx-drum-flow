from PIL import Image,ImageDraw
from pathlib import Path
from scipy.ndimage import map_coordinates
import numpy as np
r=Path('/workspace/scratch/3007f183e4a8/repo');o=r.parent/'work_output';W,H=1448,1086;n=np.array(Image.open(o/'sources/neutral.png'))
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
m=poly([(420,376),(474,380),(527,454),(576,465),(616,482),(624,535),(582,551),(540,547),(530,531),(493,529),(480,490),(420,418)]);limb=np.zeros_like(n);limb[m]=n[m]
up=poly([(610,430),(713,430),(708,465),(682,517),(600,517),(590,480)])
clear=poly([(578,469),(627,447),(679,465),(674,513),(632,557),(581,544)])
base=n.copy();base[m|up|clear]=0
src=np.zeros_like(n);src[up]=n[up];yy,xx=np.mgrid[:H,:W];sy=430+(yy-430)/.7;sx=xx-114*(sy-430)/80;upper=np.stack([map_coordinates(src[:,:,k],[sy,sx],order=1,mode='constant',cval=0) for k in range(4)],axis=2).astype('uint8');upper[:430]=0;upper[487:]=0;baseim=Image.alpha_composite(Image.fromarray(base),Image.fromarray(upper));shift=Image.new('RGBA',(W,H));shift.alpha_composite(Image.fromarray(limb),(114,-24));kit=Image.open(o/'sources/drum_fixed.png').convert('RGBA');fore=Image.open(r/'character-assets/layers/drum/drum_foreground_occlusion.png');hair=Image.open(r/'character-assets/layers/character/base/hair_foreground_source.png')
configs={'ht':{'angle':0,'scale':1,'shift':(0,0)},'lt':{'angle':122.3,'scale':.835,'shift':(0,0)},'ft':{'angle':165,'scale':1.08,'shift':(101,-16)}}
for part,c in configs.items():
 (o/f'variants/{part}').mkdir(exist_ok=True)
 for ph in ['hit','rebound']:
  angle=c['angle']+((18 if part=='ht' else -18) if ph=='rebound' else 0);a=np.radians(angle);A=c['scale']*np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]]);E=np.array([729,486]);t=E+np.array(c['shift'])-A@E;M=np.vstack([np.column_stack([A,t]),[0,0,1]]);iv=np.linalg.inv(M);moving=shift.transform((W,H),Image.Transform.AFFINE,tuple(iv[:2].ravel()),Image.Resampling.BICUBIC);im=Image.alpha_composite(baseim,moving);im.save(o/f'variants/{part}/{ph}_l_source_candidate.png');ar=np.array(im);bg=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(W,H),'white'),kit),im);bg=Image.alpha_composite(bg,fore);df=np.any(ar!=n,axis=2);front=np.zeros_like(ar);front[df]=ar[df];bg=Image.alpha_composite(bg,Image.fromarray(front));bg=Image.alpha_composite(bg,hair);bg.save(o/f'previews/{part}_l_{ph}.png');print(part,ph,'tip',A@np.array([558,373])+t,'grip',A@np.array([633,466])+t)
