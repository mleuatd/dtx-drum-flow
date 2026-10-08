from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
O=Path('work_output');qa={};base=np.array(Image.open('repo/character-assets/layers/character/base/neutral.png').convert('RGBA'));drum=Image.open('work/01_reference/DRUM_FIXED_ORIGINAL_1448x1086.png').convert('RGBA')
for p in ['hit','rebound']:
 a=np.array(Image.open(O/'variants/sn'/f'{p}_l_candidate_v1.png'));b=np.array(Image.open(O/'variants/sn'/f'{p}_l_candidate_v2.png'))
 mask=Image.new('L',(1448,1086));ImageDraw.Draw(mask).polygon([(563,486),(606,461),(645,477),(656,513),(633,544),(602,552),(565,545)],fill=255);m=np.array(mask)>0;a[m]=b[m];im=Image.fromarray(a);fn=O/'variants/sn'/f'{p}_l_candidate_v3.png';im.save(fn)
 bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(drum);bg.alpha_composite(im);bg.convert('RGB').save(O/'previews'/f'sn_l_{p}_fixed_drum_v3.png')
 bg.crop((380,370,700,630)).save(O/'qa'/f'sn_l_{p}_arm_crop_v3.png');diff=np.any(a!=base,axis=2);Image.fromarray((diff*255).astype('uint8')).save(O/'qa'/f'sn_l_{p}_diff_v3.png');qa[p]={'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'changed_pixels':int(diff.sum()),'visual_status':'PENDING'}
ims=[]
for p in ['neutral','hit','rebound','neutral']:
 if p=='neutral':
  bg=Image.new('RGBA',drum.size,'white');bg.alpha_composite(drum);bg.alpha_composite(Image.fromarray(base));ims.append(bg.convert('RGB'))
 else:ims.append(Image.open(O/'previews'/f'sn_l_{p}_fixed_drum_v3.png'))
ims[0].save(O/'previews/sn_l_neutral_hit_rebound_v3.gif',save_all=True,append_images=ims[1:],duration=[350,160,220,350],loop=0)
(O/'qa/sn_l_candidate_v3.json').write_text(json.dumps(qa,indent=2))
