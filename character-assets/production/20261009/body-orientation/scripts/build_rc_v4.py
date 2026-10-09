from pathlib import Path
import cv2, numpy as np, json, hashlib
from PIL import Image
R=Path(__file__).resolve().parents[5]
O=R/'character-assets/production/20261009/body-orientation'
base=np.array(Image.open(R/'character-assets/layers/character/rc/hit_r_refresh.png').convert('RGBA'))
donor=np.array(Image.open(O/'candidates/rc_hit_registered_v3.png').convert('RGBA'))
h,w=base.shape[:2]
def white(a):return (a[:,:,:3].astype(float)*a[:,:,3:4]/255+255*(1-a[:,:,3:4]/255)).astype('uint8')
# Dense registration is restricted to the lower hair junction; hands are never flipped.
bg=cv2.cvtColor(white(base),cv2.COLOR_RGB2GRAY); dg=cv2.cvtColor(white(donor),cv2.COLOR_RGB2GRAY)
flow=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM).calc(bg,dg,None)
y,x=np.mgrid[:h,:w].astype('float32');strength=np.clip((y-410)/130,0,1)
warped=cv2.remap(donor,x+flow[:,:,0]*strength,y+flow[:,:,1]*strength,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
a=base.copy();mask=(y<590)&(x>595)&(x<1090)
# Broad head/shoulder replacement, confined by the original forearm and left sleeve.
mask &= ((y<300)|((x>700)&(y<455))|((x>700)&(y>=455)))
alpha=np.clip((580-y)/60,0,1)
a[mask]=((warped*alpha[:,:,None]+base*(1-alpha[:,:,None]))[mask]).astype('uint8')
a[590:]=base[590:]
Image.fromarray(a).save(O/'candidates/rc_hit_v4.png')
drum=Image.open(R/'character-assets/layers/drum/drum_base.png').convert('RGBA')
b=Image.new('RGBA',(w,h),'white');b.alpha_composite(drum);b.alpha_composite(Image.fromarray(a));b.convert('RGB').save(O/'qa/rc_hit_composite_v4.png')
b.crop((560,250,1090,670)).resize((795,630)).save(O/'qa/rc_hit_join_v4.png')
(O/'qa/rc_v4_mechanical.json').write_text(json.dumps({'status':'PENDING_VISUAL_REVIEW','lower_y590_equal':bool(np.array_equal(a[590:],base[590:])), 'right_hand_and_contact_equal':bool(np.array_equal(a[:450,1090:],base[:450,1090:]))},indent=2))
