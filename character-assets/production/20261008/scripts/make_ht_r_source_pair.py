from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json
r=Path('/workspace/scratch/3007f183e4a8/repo');o=r.parent/'work_output';n=np.array(Image.open(r/'character-assets/layers/character/sn/hit_l.png'));hh=np.array(Image.open(r/'character-assets/layers/character/hh/hit_r.png'));don=np.array(Image.open(r/'character-assets/production/20261008/donors/right_arm_donor.png'))
def poly(p):
 m=Image.new('L',(1448,1086));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
near=poly([(650,317),(710,320),(716,392),(699,465),(674,513),(632,557),(602,548),(581,526),(587,486),(613,467),(622,414)])&(n[:,:,3]>0)
dm=poly([(345,405),(472,399),(525,401),(560,395),(633,378),(642,425),(606,462),(558,475),(475,482),(343,445)])&~near
move=np.zeros_like(hh);move[dm]=hh[dm];base=n.copy();old=poly([(975,412),(995,409),(1045,306),(1068,307),(1070,342),(1036,407),(1044,458),(1012,486),(998,492),(985,453),(975,435)]);base[old]=don[old]
shift=Image.new('RGBA',(1448,1086));shift.alpha_composite(Image.fromarray(move),(198,-48));o.joinpath('variants/ht').mkdir(exist_ok=True)
kit=Image.open(o/'sources/drum_fixed.png').convert('RGBA');fore=Image.open(r/'character-assets/layers/drum/drum_foreground_occlusion.png');hair=Image.open(r/'character-assets/layers/character/base/hair_foreground_source.png')
for ph in ['hit','rebound']:
 limb=shift if ph=='hit' else shift.rotate(-17,Image.Resampling.BICUBIC,center=(828,362));a=np.array(Image.alpha_composite(Image.fromarray(base),limb));a[near]=n[near];im=Image.fromarray(a);im.save(o/f'variants/ht/{ph}_r_source_candidate.png');bg=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(1448,1086),'white'),kit),im);bg=Image.alpha_composite(bg,fore);front=np.zeros_like(a);diff=np.any(a!=np.array(Image.open(o/'sources/neutral.png')),axis=2);front[diff]=a[diff];bg=Image.alpha_composite(bg,Image.fromarray(front));bg=Image.alpha_composite(bg,hair);bg.save(o/f'previews/ht_r_{ph}.png')
print('HT:R candidate; wholly hidden hand exempt, visible stick target560375')
