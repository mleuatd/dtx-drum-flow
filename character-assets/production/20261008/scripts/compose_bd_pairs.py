from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
r=Path('/workspace/scratch/3007f183e4a8/repo');o=r.parent/'work_output'; inv=json.loads((r/'character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json').read_text());n=np.array(Image.open(o/'sources/neutral.png'))
mp={'BD:RF':None,'BD+RC:RF/R':'RC:R','BD+SN:RF/L':'SN:L','BD+SN:RF/R':'SN:R','BD+RD:RF/R':'RD:R','BD+HH:RF/R':'HH:R','BD+LT:RF/R':'LT:R','BD+HH+SN:RF/R/L':'HH+SN:R/L','BD+RC+SN:RF/R/L':'RC+SN:R/L'}
kit=Image.open(o/'sources/drum_fixed.png').convert('RGBA');sheet=Image.new('RGB',(724*2,590*9),'white');draw=ImageDraw.Draw(sheet);qa=[]
for row,(key,armkey) in enumerate(mp.items()):
 for col,ph in enumerate(['hit','rebound']):
  foot=np.array(Image.open(o/f'variants/bd/{ph}_rf_source_candidate.png')); fd=np.any(foot!=n,axis=2)
  arm=n.copy() if armkey is None else np.array(Image.open(r/'character-assets'/inv['requiredFrames'][inv['runtimePhaseFrameMap'][armkey][ph]]['path']))
  assert not np.any(fd & np.any(arm!=n,axis=2));a=arm.copy();a[fd]=foot[fd];name=key.replace(':','_').replace('/','_').replace('+','_')+'_'+ph+'.png';Image.fromarray(a).save(o/'variants/bd'/name)
  assert np.array_equal(a[:700],arm[:700]);assert np.array_equal(a[:,0:560],arm[:,0:560]);assert np.array_equal(a[:,800:],arm[:,800:])
  im=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(1448,1086),'white'),kit),Image.fromarray(a));im=im.resize((724,543));sheet.paste(im,(col*724,row*590+30));draw.text((col*724+10,row*590+10),key+' '+ph,fill='black')
  qa.append({'key':key,'phase':ph,'candidate':name,'arm_foot_delta_overlap':0,'outside_foot_region_mismatch':0,'foot_region':[560,730,800,1000]})
sheet.save(o/'qa/bd_nine_pairs_sheet.png');(o/'qa/bd_nine_pairs_mechanical.json').write_text(json.dumps(qa,indent=2));print('18 candidate frames; protected upper body/near leg exact; disjoint source-bound arm/foot changes')
