#!/usr/bin/env python3
"""Verify actual PNG bytes for the reviewed 2026-10-08 SN:L pair."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parents[2];A=R/'character-assets/layers';n=Image.open(A/'character/base/neutral.png').convert('RGBA');size=(1448,1086)
source_mask=Image.new('L',size);ImageDraw.Draw(source_mask).polygon([(420,376),(474,380),(527,454),(576,465),(616,482),(624,535),(582,551),(540,547),(530,531),(493,529),(480,490),(420,418)],fill=255)
sleeve=Image.new('L',size);ImageDraw.Draw(sleeve).polygon([(563,486),(606,461),(645,477),(656,513),(633,544),(602,552),(565,545)],fill=255)
records=[]
for phase,angle in [('hit',47),('rebound',15)]:
 p=A/f'character/sn/{phase}_l.png';im=Image.open(p).convert('RGBA');rot=source_mask.rotate(angle,Image.Resampling.NEAREST,center=(615,510),expand=False);allowed=[bool(a or b or c) for a,b,c in zip(source_mask.getdata(),rot.getdata(),sleeve.getdata())];outside=changed=0
 for a,b,ok in zip(n.getdata(),im.getdata(),allowed):
  if a!=b:
   changed+=1
   if not ok:outside+=1
 records.append({'phase':phase,'canvas':list(im.size),'outside_allowed_roi_changed_pixels':outside,'changed_pixels':changed,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pass':im.size==size and outside==0 and changed>1000 and im.getchannel('A').getextrema()[0]==0})
drum_sha=hashlib.sha256((A/'drum/drum_base.png').read_bytes()).hexdigest();result={'records':records,'drum_sha256':drum_sha,'pass':all(x['pass'] for x in records) and drum_sha=='dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85','scope':'Actual bytes and protected regions. Visual anatomy/contact QA is separately recorded in production/20261008/qa.'};print(json.dumps(result,indent=2));raise SystemExit(0 if result['pass'] else 1)
