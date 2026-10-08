from PIL import Image,ImageDraw
import numpy as np,json
from pathlib import Path
O=Path('work_output');source=np.array(Image.open(O/'variants/sn/hit_l_candidate_v3.png').convert('RGBA'));hit=np.array(Image.open(O/'variants/hh/hit_r_local_edit_v3.png').convert('RGBA'));near=Image.new('L',(1448,1086));ImageDraw.Draw(near).polygon([(650,317),(710,320),(716,392),(699,465),(674,513),(632,557),(602,548),(581,526),(587,486),(613,467),(622,414)],fill=255);nm=(np.array(near)>0)&(source[:,:,3]>0);hit[nm]=source[nm]
dist=Image.new('L',(1448,1086));ImageDraw.Draw(dist).polygon([(345,405),(472,399),(525,401),(560,395),(633,378),(642,425),(606,462),(558,475),(475,482),(343,445)],fill=255);dm=(np.array(dist)>0)&~nm;moving=np.zeros_like(hit);moving[dm]=hit[dm];fixed=hit.copy();fixed[dm]=0;rot=Image.fromarray(moving).rotate(-17,Image.Resampling.BICUBIC,center=(630,410),expand=False);reb=np.array(Image.alpha_composite(Image.fromarray(fixed),rot));reb[nm]=source[nm]
for phase,a in [('hit',hit),('rebound',reb)]:
 im=Image.fromarray(a);im.save(O/f'variants/hh/{phase}_r_local_edit_v4.png');dr=Image.open(O/'sources/drum_fixed.png').convert('RGBA');bg=Image.new('RGBA',dr.size,'white');bg.alpha_composite(dr);bg.alpha_composite(im);bg.convert('RGB').save(O/f'previews/hh_r_{phase}_local_edit_v4.png')
