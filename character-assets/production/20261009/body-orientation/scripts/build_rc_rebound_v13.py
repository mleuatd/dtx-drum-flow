from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[5];O=R/'character-assets/production/20261009/body-orientation'
hit=np.array(Image.open(O/'candidates/rc_hit_v8.png').convert('RGBA'));base=np.array(Image.open(R/'character-assets/layers/character/rc/rebound_r_refresh.png').convert('RGBA'));a=hit.copy();a[:430,1000:]=base[:430,1000:];a[590:]=base[590:]
Image.fromarray(a).save(O/'candidates/rc_rebound_v13.png');dr=Image.open(R/'character-assets/layers/drum/drum_base.png').convert('RGBA');bg=Image.new('RGBA',dr.size,'white');bg.alpha_composite(dr);bg.alpha_composite(Image.fromarray(a));bg.convert('RGB').save(O/'qa/rc_rebound_composite_v13.png')
(O/'qa/rc_rebound_v13_mechanical.json').write_text(json.dumps({'status':'PENDING_VISUAL_REVIEW','lower_y590_equal':bool(np.array_equal(a[590:],base[590:])), 'distal_arm_equal':bool(np.array_equal(a[:430,1000:],base[:430,1000:])), 'paired_torso_equal':bool(np.array_equal(a[:590,:1000],hit[:590,:1000]))},indent=2))
ims=[]
for p in ['rc_hit_composite_v8.png','rc_rebound_composite_v13.png']:ims.append(Image.open(O/'qa'/p))
ims[0].save(O/'qa/rc_v8_v13_review_motion.gif',save_all=True,append_images=ims[1:],duration=[160,220],loop=0)
