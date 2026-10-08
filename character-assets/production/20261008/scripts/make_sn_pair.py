from PIL import Image,ImageDraw
import numpy as np,math,json,hashlib
from pathlib import Path
out=Path('work_output');(out/'variants/sn').mkdir(exist_ok=True)
src=Path('repo/character-assets/layers/character/base/neutral.png');base=Image.open(src).convert('RGBA');drum=Image.open('work/01_reference/DRUM_FIXED_ORIGINAL_1448x1086.png').convert('RGBA')
mask=Image.new('L',base.size);ImageDraw.Draw(mask).polygon([(420,376),(474,380),(527,454),(576,465),(616,482),(624,535),(582,551),(540,547),(530,531),(493,529),(480,490),(420,418)],fill=255)
a=np.array(base);m=np.array(mask)>0;limb=np.zeros_like(a);limb[m]=a[m];fixed=a.copy();fixed[m]=0;pivot=(615,510);qa={}
for phase,angle in [('hit',47),('rebound',15)]:
 moving=Image.fromarray(limb).rotate(angle,resample=Image.Resampling.BICUBIC,center=pivot,expand=False);candidate=Image.alpha_composite(Image.fromarray(fixed),moving)
 # Preserve all RGBA bytes outside source and transformed mask, including hidden RGB.
 tm=np.array(mask.rotate(angle,resample=Image.Resampling.NEAREST,center=pivot))>0;ca=np.array(candidate);ca[~(m|tm)]=a[~(m|tm)];candidate=Image.fromarray(ca)
 candidate.save(out/'variants/sn'/f'{phase}_l_candidate_v1.png');comp=Image.alpha_composite(drum,candidate);bg=Image.new('RGBA',base.size,'white');bg.alpha_composite(comp);bg.convert('RGB').save(out/'previews'/f'sn_l_{phase}_fixed_drum_v1.png')
 theta=-math.radians(angle)
 def trans(p):
  x,y=p[0]-pivot[0],p[1]-pivot[1];return [round(pivot[0]+math.cos(theta)*x-math.sin(theta)*y,2),round(pivot[1]+math.sin(theta)*x+math.cos(theta)*y,2)]
 diff=np.any(ca!=a,axis=2);Image.fromarray((diff*255).astype('uint8')).save(out/'qa'/f'sn_l_{phase}_diff_v1.png')
 qa[phase]={'tip':trans((444,394)),'grip':trans((519,490)),'wrist':trans((553,509)),'elbow':list(pivot),'changed_pixels':int(diff.sum()),'outside_edit_roi_changed_pixels':int(np.any(ca[~(m|tm)]!=a[~(m|tm)],axis=1).sum()),'rotation':angle,'visual_status':'PENDING'}
frames=[Image.open(out/'previews'/f'sn_l_{p}_fixed_drum_v1.png') for p in ['rebound','hit','rebound']];frames[0].save(out/'previews/sn_l_pair_candidate_v1.gif',save_all=True,append_images=frames[1:],duration=[300,140,260],loop=0)
qa['source_sha256']=hashlib.sha256(src.read_bytes()).hexdigest();qa['status']='CANDIDATE';(out/'qa/sn_l_candidate_v1.json').write_text(json.dumps(qa,indent=2));print(qa)
