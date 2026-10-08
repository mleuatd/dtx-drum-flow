from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np
r=Path('/workspace/scratch/3007f183e4a8/repo');o=r.parent/'work_output';n=np.array(Image.open(o/'sources/neutral.png'));W,H=1448,1086
m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon([(420,376),(474,380),(527,454),(576,465),(616,482),(624,535),(582,551),(540,547),(530,531),(493,529),(480,490),(420,418)],fill=255);mask=np.array(m)>0;limb=np.zeros_like(n);limb[mask]=n[mask];base=n.copy();base[mask]=0
# Clear old elbow/cuff transition only below protected shoulder sleeve.
clear=Image.new('L',(W,H));ImageDraw.Draw(clear).polygon([(578,469),(627,447),(679,465),(674,513),(632,557),(581,544)],fill=255);cm=np.array(clear)>0;base[cm]=0
shift=Image.new('RGBA',(W,H));shift.alpha_composite(Image.fromarray(limb),(114,-24));kit=Image.open(o/'sources/drum_fixed.png').convert('RGBA');fore=Image.open(r/'character-assets/layers/drum/drum_foreground_occlusion.png');hair=Image.open(r/'character-assets/layers/character/base/hair_foreground_source.png');(o/'variants/ht').mkdir(exist_ok=True)
for ph in ['hit','rebound']:
 l=shift if ph=='hit' else shift.rotate(-18,Image.Resampling.BICUBIC,center=(729,486));im=Image.alpha_composite(Image.fromarray(base),l);im.save(o/f'variants/ht/{ph}_l_source_candidate.png');a=np.array(im);bg=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(W,H),'white'),kit),im);bg=Image.alpha_composite(bg,fore);front=np.zeros_like(a);df=np.any(a!=n,axis=2);front[df]=a[df];bg=Image.alpha_composite(bg,Image.fromarray(front));bg=Image.alpha_composite(bg,hair);bg.save(o/f'previews/ht_l_{ph}.png')
print('Candidate HT left tip558370; visible sleeve seam must be checked')
