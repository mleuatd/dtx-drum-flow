from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,math,json
O=Path('work_output');base=np.array(Image.open(O/'variants/sn/hit_l_candidate_v3.png'));old=np.array(Image.open(O/'variants/hh/hit_r_local_edit_v4.png'));g=np.array(Image.open('generated_images/exec-bc8e64f2-3b5f-4d6d-8d4b-4fc8213331d8.png').convert('RGBA'))
om=Image.new('L',(1448,1086));ImageDraw.Draw(om).polygon([(975,412),(995,409),(1045,306),(1068,307),(1070,342),(1036,407),(1044,458),(1012,486),(998,492),(985,453),(975,435)],fill=255);o=np.array(om)>0;base[o]=old[o]
m=Image.new('L',(1448,1086));ImageDraw.Draw(m).polygon([(909,329),(950,346),(988,379),(1010,394),(1053,378),(1067,372),(1093,388),(1106,409),(1102,440),(1062,469),(1010,476),(969,448),(944,409),(922,376),(945,323),(957,306),(977,322),(1042,373)],fill=255);don=np.zeros_like(g);don[np.array(m)>0]=g[np.array(m)>0]
# Rigid local motion relocates the candidate's inaccurate tip to the actual low-tom head.
# Grip (1066,407), tip (959,319); rotation -12 deg, translation calibrated to tip885416.
c=(1066,407);ang=12;theta=-math.radians(ang);M=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);tip=np.array(c)+M.dot(np.array([959,319])-c);shift=np.array([885,416])-tip
sm=Image.new('L',(1448,1086));ImageDraw.Draw(sm).polygon([(949,310),(962,306),(1051,379),(1063,373),(1085,380),(1099,400),(1100,423),(1089,439),(1069,440),(1039,417),(1036,397)],fill=255);ImageDraw.Draw(sm).ellipse((946,306,970,332),fill=255);stick=np.zeros_like(g);stick[np.array(sm)>0]=g[np.array(sm)>0]
hair=Image.new('L',(1448,1086));ImageDraw.Draw(hair).polygon([(875,260),(921,300),(977,388),(995,455),(987,526),(951,625),(900,656),(842,566),(820,385)],fill=255);protect=(np.array(hair)>0)&(base[:,:,3]>0)
for phase,extra in [('hit',0),('rebound',-18)]:
 rotated=Image.fromarray(don).rotate(ang+extra,Image.Resampling.BICUBIC,center=c);temp=Image.new('RGBA',(1448,1086));temp.alpha_composite(rotated,tuple(np.rint(shift).astype(int)));a=np.array(Image.alpha_composite(Image.fromarray(base),temp));a[protect]=base[protect];top=Image.new('RGBA',(1448,1086));top.alpha_composite(Image.fromarray(stick).rotate(ang+extra,Image.Resampling.BICUBIC,center=c),tuple(np.rint(shift).astype(int)));a=np.array(Image.alpha_composite(Image.fromarray(a),top));im=Image.fromarray(a);(O/'variants/lt').mkdir(exist_ok=True);im.save(O/f'variants/lt/{phase}_r_local_v1.png');dr=Image.open(O/'sources/drum_fixed.png').convert('RGBA');bg=Image.new('RGBA',dr.size,'white');bg.alpha_composite(dr);bg.alpha_composite(im);bg.convert('RGB').save(O/f'previews/lt_r_{phase}_local_v1.png')
print('shift',shift,'grip',np.array(c)+shift)
