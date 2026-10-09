from pathlib import Path
import numpy as np,json
from PIL import Image
R=Path(__file__).resolve().parents[5];O=R/'character-assets/production/20261009/body-orientation'
b=np.array(Image.open(R/'character-assets/layers/character/rc/hit_r_refresh.png').convert('RGBA'));d=np.array(Image.open(O/'candidates/rc_hit_registered_v3.png').convert('RGBA'))
# Find a connected low-ink seam through the lower hair, never the protected legs.
def white(a):return a[:,:,:3].mean(2)*a[:,:,3]/255+255*(1-a[:,:,3]/255)
f=white(b);g=white(d);x0,x1,y0,y1=650,1050,465,585
cost=abs(f[y0:y1,x0:x1]-g[y0:y1,x0:x1])+2*(255-np.minimum(f[y0:y1,x0:x1],g[y0:y1,x0:x1]))
H,W=cost.shape;acc=cost[:,0].copy();back=np.zeros((H,W),int)
for x in range(1,W):
 for y in range(H):
  ids=np.arange(max(0,y-1),min(H,y+2));idx=ids[np.argmin(acc[ids])];back[y,x]=idx
 old=acc.copy();acc=np.array([cost[y,x]+old[back[y,x]] for y in range(H)])
s=np.zeros(W,int);s[-1]=np.argmin(acc)
for x in range(W-1,0,-1):s[x-1]=back[s[x],x]
seam=np.full(1448,550);seam[x0:x1]=s+y0
out=b.copy();Y,X=np.mgrid[:1086,:1448];mask=(Y<seam[X])&(X<1090)
out[mask]=d[mask]
# Original distal forearm, wrist, hand and stick remain exact.
keep=(X>1030)&(Y<340);out[keep]=b[keep]
out[590:]=b[590:]
Image.fromarray(out).save(O/'candidates/rc_hit_v5.png')
dr=Image.open(R/'character-assets/layers/drum/drum_base.png').convert('RGBA');im=Image.new('RGBA',dr.size,'white');im.alpha_composite(dr);im.alpha_composite(Image.fromarray(out));im.convert('RGB').save(O/'qa/rc_hit_composite_v5.png')
Image.fromarray((mask*255).astype('uint8')).save(O/'qa/upper_body_mask_v5.png')
(O/'qa/rc_v5_mechanical.json').write_text(json.dumps({'status':'PENDING_VISUAL_REVIEW','lower_y590_equal':bool(np.array_equal(out[590:],b[590:])), 'distal_right_arm_equal':bool(np.array_equal(out[keep],b[keep])), 'seam_range':[int(seam[x0:x1].min()),int(seam[x0:x1].max())]},indent=2))
