from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np
O=Path('work_output');dr=Image.open(O/'sources/drum_fixed.png').convert('RGBA');n=np.array(Image.open(O/'sources/neutral.png').convert('RGBA'));m=Image.new('L',dr.size);d=ImageDraw.Draw(m)
for pts in [[(604,252),(716,215),(774,207),(778,176),(817,173),(830,211),(966,216),(1001,280),(975,312),(854,346),(687,334),(610,315)],[(735,405),(773,380),(895,378),(967,399),(995,425),(979,489),(961,566),(893,585),(780,570),(727,553)],[(346,542),(377,518),(541,508),(619,522),(642,551),(614,684),(572,707),(404,700),(355,665)]]:d.polygon(pts,fill=255)
# Leaning head is in front of the left portion of ride; torso/hair below remain behind.
ImageDraw.Draw(m).polygon([(560,100),(731,100),(731,288),(704,311),(560,311)],fill=0)
a=np.array(dr);a[np.array(m)==0]=0;fore=Image.fromarray(a);fore.save(O/'sources/drum_foreground_occlusion.png');m.save(O/'qa/drum_foreground_mask.png')
am=Image.new('L',dr.size);ad=ImageDraw.Draw(am);ad.polygon([(420,376),(474,380),(527,454),(575,465),(615,450),(630,370),(648,317),(710,320),(716,392),(699,465),(674,513),(632,557),(602,548),(581,552),(530,551),(493,529),(480,490),(420,418)],fill=255);ad.polygon([(1048,308),(1068,310),(1038,401),(1043,466),(1008,475),(984,455),(974,432),(989,415),(1004,414)],fill=255);arm=np.array(am)>0
for name,path in [('neutral','sources/neutral.png'),('hh_sn','variants/combo/hh_sn_r_l_hit_v1.png'),('rc','variants/rc/hit_r_local_v1.png'),('rd','variants/rd/hit_r_local_v2.png'),('lt_hit','variants/lt/hit_r_local_v1.png'),('lt_rebound','variants/lt/rebound_r_local_v1.png')]:
 c=np.array(Image.open(O/path).convert('RGBA'));move=np.any(c!=n,axis=2)|arm;front=c.copy();front[~move]=0;bg=Image.new('RGBA',dr.size,'white');bg.alpha_composite(dr);bg.alpha_composite(Image.fromarray(c));bg.alpha_composite(fore);bg.alpha_composite(Image.fromarray(front));bg.convert('RGB').save(O/f'previews/occlusion_{name}.png')
