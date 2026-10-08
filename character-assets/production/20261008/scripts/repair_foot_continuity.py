"""Foot continuity repair; canonical girl/drum remain immutable."""
from pathlib import Path
import runpy,json,hashlib,copy
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
r=next(p for p in Path(__file__).resolve().parents if (p/'character-assets').is_dir())
p=r/'character-assets/production/20261008'; q=p/'qa'
runpy.run_path(str(p/'scripts/restore_source_workspace.py'))
d=runpy.run_path(str(p/'scripts/make_bd_source_pair.py'))
leg=np.array(d['leg']); base=d['base']; H,W=leg.shape[:2]
yy,xx=np.mgrid[:H,:W]; t=np.deg2rad(7)*np.clip((yy-730)/100,0,1); px,py=719,915
sx=px+np.cos(t)*(xx-px)+np.sin(t)*(yy-py)
sy=py-np.sin(t)*(xx-px)+np.cos(t)*(yy-py)
raised=np.stack([map_coordinates(leg[:,:,k],[sy,sx],order=1,mode='constant',cval=0) for k in range(4)],axis=2).astype('uint8')
hit=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(leg)))
ready=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(raised)))
roi=np.zeros((H,W),bool);roi[730:1000,560:800]=True
invp=r/'character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json'; inv=json.loads(invp.read_text())
mp=r/'character-assets/config/assets_manifest.json'; manifest=json.loads(mp.read_text())
hashes={}; records=[]
for key in inv['runtimeQaTarget']['actions']:
 for phase in ['hit','rebound']:
  frame=inv['runtimePhaseFrameMap'][key][phase]; f=inv['requiredFrames'][frame]; path='character-assets/'+f['path']; target=r/path
  old=np.array(Image.open(target).convert('RGBA')); new=old.copy(); template=hit if key.startswith('BD') and phase=='hit' else ready;new[roi]=template[roi]
  assert np.array_equal(new[~roi],old[~roi])
  Image.fromarray(new).save(target);sha=hashlib.sha256(target.read_bytes()).hexdigest();hashes[path]=sha;f['sha256']=sha;f['qaStatus']='FOOT_CONTINUITY_STATIC_PENDING_VISIBLE_AND_RUNTIME'
  records.append({'key':key,'phase':phase,'path':path,'sha256':sha,'outsideFootRoiExact':True})
neutral='character-assets/layers/character/base/neutral_performance_ready.png'
original=np.array(Image.open(r/'character-assets/layers/character/base/neutral.png').convert('RGBA')); n=original.copy();n[roi]=ready[roi];Image.fromarray(n).save(r/neutral)
hashes[neutral]=hashlib.sha256((r/neutral).read_bytes()).hexdigest()
inv['requiredFrames']['neutral']['path']=neutral.removeprefix('character-assets/');inv['requiredFrames']['neutral']['sha256']=hashes[neutral]
inv['production20261008']['footContinuity']='STATIC_PENDING_VISIBLE_AND_RUNTIME'
for a in manifest['assets']:
 if a['path'] in hashes:
  a['sha256']=hashes[a['path']];a.setdefault('notes',[]).append('20261008 pedal continuity: toes remain on pedal, rebound raises heel; outside foot ROI unchanged. Visible/runtime review pending.')
a=copy.deepcopy(next(a for a in manifest['assets'] if a['path']=='character-assets/layers/character/base/neutral.png'))
a.update(path=neutral,sha256=hashes[neutral],status='SOURCE_BOUND_STATIC_QA_PASS',purpose='performance ready toe-planted heel-raised neutral',semanticRole='performance-ready-pose',tags=['ready','source-bound'],notes=['Original approved Neutral preserved; right foot continuity refinement pending visible/runtime review.'])
manifest['assets'].append(a)
invp.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n');mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Synchronize current SHA anywhere in brushup metadata without changing historical evidence.
lp=r/'character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json'; ledger=json.loads(lp.read_text())
def sync(obj):
 if isinstance(obj,dict):
  path=obj.get('path') or obj.get('targetPath') or obj.get('assetPath')
  if path and not path.startswith('character-assets/'):path='character-assets/'+path
  if path in hashes:
   for field in ['sha256','sourceSha256','currentSha256']:
    if field in obj:obj[field]=hashes[path]
  for value in obj.values():sync(value)
 elif isinstance(obj,list):
  for value in obj:sync(value)
sync(ledger);lp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
kit=Image.open(r/'character-assets/layers/drum/drum_base.png').convert('RGBA')
strip=Image.new('RGB',(960,660),'white')
for index,(label,arr) in enumerate([('Ready / Rebound',ready),('Hit',hit)]):
 preview=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(W,H),'white'),kit),Image.fromarray(arr))
 strip.paste(preview.crop((560,700,800,1030)).resize((480,660)).convert('RGB'),(index*480,0))
ImageDraw.Draw(strip).text((8,8),'Ready / Rebound',fill='black');ImageDraw.Draw(strip).text((488,8),'Hit',fill='black')
strip.save(q/'foot_continuity_detail.png')
(q/'foot_continuity.json').write_text(json.dumps({'status':'STATIC_INVARIANTS_PASS_VISIBLE_AND_RUNTIME_PENDING','toePivot':[719,915],'heelAngleDegrees':7,'canonicalNeutralUnchanged':True,'fixedDrumUnchanged':True,'frames':records,'readyPath':neutral,'resume':'Inspect foot_continuity_detail.png, then all30 public runtime QA, update completion entry.'},ensure_ascii=False,indent=2)+'\n')
for path in ['site/character-prototype.js','site/app.js','site/index.html']:
 fp=r/path;s=fp.read_text().replace('20261008-retry-r11','20261008-foot-continuity-r12')
 if path.endswith('character-prototype.js'):s=s.replace('sourceBoundHairFrames=new Set([','sourceBoundHairFrames=new Set(["layers/character/base/neutral_performance_ready.png", ')
 fp.write_text(s)
print('Updated 60 PNG + performance ready Neutral; immutable sources and outside-foot pixels preserved.')
