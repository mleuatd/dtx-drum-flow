from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,os,tempfile
r=Path('/workspace/scratch/3007f183e4a8/repo');o=r.parent/'work_output';inv=json.loads((r/'character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json').read_text());n=np.array(Image.open(o/'sources/neutral.png'));lh=np.array(Image.open(r/'character-assets/layers/character/sn/hit_l.png'));lr=np.array(Image.open(r/'character-assets/layers/character/sn/rebound_l.png'));ld=np.any(lh!=lr,axis=2)
mp={'HT:R':('ht','r',False,False),'HT:L':('ht','l',False,False),'LT:L':('lt','l',False,False),'FT:R':('ft','r',False,False),'FT:L':('ft','l',False,False),'FT+SN:R/L':('ft','r',False,True),'BD+HT:RF/R':('ht','r',True,False),'BD+HT:RF/L':('ht','l',True,False),'BD+FT:RF/L':('ft','l',True,False),'BD+FT:RF/R':('ft','r',True,False),'BD+FT+SN:RF/R/L':('ft','r',True,True)}
out=o/'variants/remaining';out.mkdir(exist_ok=True);kit=Image.open(o/'sources/drum_fixed.png').convert('RGBA');fore=Image.open(r/'character-assets/layers/drum/drum_foreground_occlusion.png');hair=Image.open(r/'character-assets/layers/character/base/hair_foreground_source.png');sheet=Image.new('RGB',(1014*2,800*11),'white');d=ImageDraw.Draw(sheet);records=[]
for row,(key,(part,hand,bd,sn)) in enumerate(mp.items()):
 for col,ph in enumerate(['hit','rebound']):
  a=np.array(Image.open(o/f'variants/{part}/{ph}_{hand}_source_candidate.png'));assert np.array_equal(a[650:],n[650:])
  if sn and ph=='rebound':a[ld]=lr[ld]
  if bd:
   foot=np.array(Image.open(r/'character-assets/layers/character/bd'/f'{ph}_rf.png'));fd=np.any(foot!=n,axis=2);assert not np.any(fd&np.any(a!=n,axis=2));a[fd]=foot[fd]
  fname=key.replace(':','_').replace('/','_').replace('+','_')+'_'+ph+'.png';tmp=Path(tempfile.gettempdir())/fname;Image.fromarray(a).save(tmp);Image.open(tmp).load();os.replace(tmp,out/fname)
  bg=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(1448,1086),'white'),kit),Image.fromarray(a));bg=Image.alpha_composite(bg,fore);front=np.zeros_like(a);df=np.any(a!=n,axis=2);front[df]=a[df];bg=Image.alpha_composite(bg,Image.fromarray(front));bg=Image.alpha_composite(bg,hair);bg.resize((1014,760)).convert('RGB').save(o/'qa'/f'{fname}.jpg');sheet.paste(bg.resize((1014,760)).convert('RGB'),(col*1014,row*800+30));d.text((col*1014+10,row*800+10),key+' '+ph,fill='black');records.append({'key':key,'phase':ph,'candidate':fname,'arm_foot_overlap':0,'legs_source_exact_unless_BD':True})
sheet.resize((1014,4400)).save(o/'qa/remaining_11_pairs_sheet.jpg');(o/'qa/remaining_11_records.json').write_text(json.dumps(records,indent=2));print('22 frames composed, protected legs/body and independent foot delta checked. Visible image QA pending.')
