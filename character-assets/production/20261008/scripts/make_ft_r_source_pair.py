from PIL import Image,ImageDraw
import numpy as np
from pathlib import Path
r=next(p for p in Path(__file__).resolve().parents if (p/'character-assets').is_dir());o=r.parent/'work_output'; n=np.array(Image.open(r/'character-assets/layers/character/sn/hit_l.png'))
b=np.array(Image.open(r/'character-assets/production/20261008/donors/right_arm_donor.png'))
def poly(p):
 m=Image.new('L',(1448,1086));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
old=poly([(975,412),(995,409),(1045,306),(1068,307),(1070,342),(1036,407),(1044,458),(1012,486),(998,492),(985,453),(975,435)]);base=n.copy();base[old]=b[old]
donor=Image.open(r/'character-assets/production/20261008/donors/right_ft_arm_candidate.png').convert('RGBA');da=np.array(donor);g=np.mean(da[:,:,:3],axis=2).astype('uint8');da[:,:,:3]=g[:,:,None];da[:565]=0;donor=Image.fromarray(da)
a=np.radians(10);A=.5*np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]]);t=np.array([1055,480])-A@np.array([929,655]);M=np.vstack([np.column_stack([A,t]),[0,0,1]]);iv=np.linalg.inv(M);arm=donor.transform((1448,1086),Image.Transform.AFFINE,tuple(iv[:2].ravel()),Image.Resampling.BICUBIC);aa=np.array(arm);aa[:350]=0;aa[:, :970]=0;arm=Image.fromarray(aa)
kit=Image.open(o/'sources/drum_fixed.png').convert('RGBA');fore=Image.open(r/'character-assets/layers/drum/drum_foreground_occlusion.png');hair=Image.open(r/'character-assets/layers/character/base/hair_foreground_source.png');(o/'variants/ft').mkdir(exist_ok=True)
for ph in ['hit','rebound']:
 limb=arm if ph=='hit' else arm.rotate(18,Image.Resampling.BICUBIC,center=(948,425));im=Image.alpha_composite(Image.fromarray(base),limb);im.save(o/f'variants/ft/{ph}_r_source_candidate.png');bg=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(1448,1086),'white'),kit),im);bg=Image.alpha_composite(bg,fore);fa=np.array(im);front=np.zeros_like(fa);diff=np.any(fa!=np.array(Image.open(o/'sources/neutral.png')),axis=2);front[diff]=fa[diff];bg=Image.alpha_composite(bg,Image.fromarray(front));bg=Image.alpha_composite(bg,hair);bg.save(o/f'previews/ft_r_{ph}.png')
print('FT:R local right arm candidate tip approximately1166,555; shoulder obscured by source hair, hidden anatomy not evaluated')
