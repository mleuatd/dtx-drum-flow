from pathlib import Path
import cv2,numpy as np,json
from PIL import Image
R=Path(__file__).resolve().parents[5];O=R/'character-assets/production/20261009/body-orientation'
b=np.array(Image.open(R/'character-assets/layers/character/rc/hit_r_refresh.png').convert('RGBA'));d=np.array(Image.open(O/'candidates/rc_hit_registered_v3.png').convert('RGBA'));h,w=b.shape[:2]
def white(a):return (a[:,:,:3].astype(float)*a[:,:,3:4]/255+255*(1-a[:,:,3:4]/255)).astype('uint8')
f=cv2.cvtColor(white(b),cv2.COLOR_RGB2GRAY);g=cv2.cvtColor(white(d),cv2.COLOR_RGB2GRAY)
flow=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM).calc(f,g,None)
flow=cv2.GaussianBlur(flow,(0,0),8)
y,x=np.mgrid[:h,:w].astype('float32');s=np.clip((y-260)/110,0,1);arm=np.clip((x-810)/70,0,1)*np.clip((430-y)/70,0,1);s*=1-arm;warp=cv2.remap(d,x+flow[:,:,0]*s,y+flow[:,:,1]*s,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
alpha=np.clip((450-y)/100,0,1);alpha=np.maximum(alpha,arm);alpha[x>1140]=0
# Preserve the original hand and exact crash contact beyond the cuff.
alpha[(x<600)&(y>530)]=0
wa=warp[:,:,3:4]/255;ba=b[:,:,3:4]/255;t=alpha[:,:,None];oa=wa*t+ba*(1-t);rgb=np.divide(warp[:,:,:3]*wa*t+b[:,:,:3]*ba*(1-t),oa,out=np.zeros_like(warp[:,:,:3],dtype=float),where=oa>0);out=np.concatenate([rgb,oa*255],axis=2).astype('uint8');out[590:]=b[590:];out[x>1140]=b[x>1140]
Image.fromarray(out).save(O/'candidates/rc_hit_v12.png')
dr=Image.open(R/'character-assets/layers/drum/drum_base.png').convert('RGBA');im=Image.new('RGBA',dr.size,'white');im.alpha_composite(dr);im.alpha_composite(Image.fromarray(out));im.convert('RGB').save(O/'qa/rc_hit_composite_v12.png')
im.crop((550,280,1100,650)).resize((1100,740)).save(O/'qa/rc_hit_join_v12.png')
(O/'qa/rc_v12_mechanical.json').write_text(json.dumps({'status':'PENDING_VISUAL_REVIEW','lower_y590_equal':bool(np.array_equal(out[590:],b[590:])), 'hit_contact_equal':bool(np.array_equal(out[:310,1120:],b[:310,1120:]))},indent=2))
