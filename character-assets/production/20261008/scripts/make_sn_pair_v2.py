from PIL import Image,ImageDraw
import numpy as np,math,json,hashlib
from scipy.ndimage import map_coordinates
from scipy.interpolate import LinearNDInterpolator
from pathlib import Path
O=Path('work_output');src=Path('repo/character-assets/layers/character/base/neutral.png');a=np.array(Image.open(src).convert('RGBA'));H,W=a.shape[:2];drum=Image.open('work/01_reference/DRUM_FIXED_ORIGINAL_1448x1086.png').convert('RGBA');qa={}
y,x=np.mgrid[340:661:5,370:721:5];points=np.column_stack([x.ravel(),y.ravel()]).astype(float);piv=np.array([615,510]);
# Field is rigid on hand/stick, smoothly tapers through the elbow/sleeve.
w=np.clip((665-points[:,0])/105,0,1);prox=points[:,0]>565;w[prox]*=np.clip((points[prox,1]-450)/40,0,1)
# Lower body and upper arm are protected.
w*=np.clip((580-points[:,1])/30,0,1)
oy,ox=np.mgrid[340:661,370:721];query=np.stack([ox,oy],axis=-1)
for phase,angle in [('hit',47),('rebound',15)]:
 t=-np.deg2rad(angle)*w;rel=points-piv;dest=np.stack([np.cos(t)*rel[:,0]-np.sin(t)*rel[:,1],np.sin(t)*rel[:,0]+np.cos(t)*rel[:,1]],axis=-1)+piv
 inv=LinearNDInterpolator(dest,points)(query);bad=np.isnan(inv[:,:,0]);inv[bad]=query[bad]
 ca=a.copy();rem=np.stack([map_coordinates(a[:,:,c].astype(float),[inv[:,:,1],inv[:,:,0]],order=1,mode='constant',cval=0) for c in range(4)],axis=-1).clip(0,255).astype('uint8');ca[340:661,370:721]=rem
 # Preserve thigh/skirt, torso/hair and rest of sleeve outside declared local polygon.
 mask=Image.new('L',(W,H));ImageDraw.Draw(mask).polygon([(420,376),(474,380),(527,454),(575,461),(618,449),(665,450),(674,546),(621,564),(590,566),(566,568),(550,590),(510,594),(383,580),(378,527),(493,450),(420,418)],fill=255)
 # Preserve known static leg below y575; donor is restricted to forearm corridor.
 mm=np.array(mask)>0;ca[~mm]=a[~mm]
 im=Image.fromarray(ca);fn=O/'variants/sn'/f'{phase}_l_candidate_v2.png';im.save(fn);bg=Image.new('RGBA',(W,H),'white');bg.alpha_composite(drum);bg.alpha_composite(im);bg.convert('RGB').save(O/'previews'/f'sn_l_{phase}_fixed_drum_v2.png')
 diff=np.any(ca!=a,axis=2);qa[phase]={'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'changed_pixels':int(diff.sum()),'outside_roi_changes':int(diff[~mm].sum()),'visual_status':'PENDING'}
ims=[Image.open(O/'previews'/f'sn_l_{p}_fixed_drum_v2.png') for p in ['rebound','hit','rebound']];ims[0].save(O/'previews/sn_l_pair_candidate_v2.gif',save_all=True,append_images=ims[1:],duration=[300,140,260],loop=0)
(O/'qa/sn_l_candidate_v2.json').write_text(json.dumps(qa,indent=2))
