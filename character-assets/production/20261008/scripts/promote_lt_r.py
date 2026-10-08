from PIL import Image
from pathlib import Path
import numpy as np,json,hashlib,shutil
O=Path('work_output');R=Path('repo');P=R/'character-assets/production/20261008';lh=np.array(Image.open(O/'variants/sn/hit_l_candidate_v3.png'));lr=np.array(Image.open(O/'variants/sn/rebound_l_candidate_v3.png'));delta=np.any(lh!=lr,axis=2)
for phase in ['hit','rebound']:
 a=np.array(Image.open(O/f'variants/lt/{phase}_r_local_v1.png'))
 if phase=='rebound':a[delta]=lr[delta]
 Image.fromarray(a).save(O/f'variants/combo/lt_sn_r_l_{phase}_v1.png')
iP=R/'character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json';inv=json.loads(iP.read_text());mP=R/'character-assets/config/assets_manifest.json';m=json.loads(mP.read_text());mat=json.loads((O/'ledger/motion_matrix.json').read_text());mapping={}
for key in ['LT:R','LT+SN:R/L']:
 for phase in ['hit','rebound']:
  f=inv['requiredFrames'][inv['runtimePhaseFrameMap'][key][phase]];t=R/'character-assets'/f['path'];src=O/(f'variants/lt/{phase}_r_local_v1.png' if key=='LT:R' else f'variants/combo/lt_sn_r_l_{phase}_v1.png');shutil.copyfile(src,t);sha=hashlib.sha256(t.read_bytes()).hexdigest();f.update(sha256=sha,state='ready',qaStatus='STATIC_VISUAL_PASS_LIVE_PENDING');mapping[str(t.relative_to(R))]=str(src)
  for asset in m['assets']:
   if asset['path']==str(t.relative_to(R)):asset.update(sha256=sha,status='SOURCE_BOUND_STATIC_QA_PASS',notes=['LT:R exact head885416; reboundtip909381; inferred hidden far shoulder/elbow; two hands no duplicated limbs'])
 for a in mat['actions']:
  if a['runtime_key']==key:a.update(status='STATIC_QA_PASSED_LIVE_PENDING',new_hit=str(mapping[str(R/'character-assets'/inv['requiredFrames'][inv['runtimePhaseFrameMap'][key]['hit']]['path']).removeprefix('repo/')]).removeprefix('work_output/'),new_rebound=str(mapping[str(R/'character-assets'/inv['requiredFrames'][inv['runtimePhaseFrameMap'][key]['rebound']]['path']).removeprefix('repo/')]).removeprefix('work_output/'))
# All first8 have now been tested live at r4. Preserve records independently.
for a in mat['actions']:
 if a['runtime_key'] in ['SN:L','SN:R','HH:R','HH+SN:R/L','RC:R','RC+SN:R/L','RD:R','RD+SN:R/L']:a.update(status='LIVE_QA_PASSED',runtime_evidence='qa/browser_post_promote_8_pairs.json')
fore=R/'character-assets/layers/drum/drum_foreground_occlusion.png';shutil.copyfile(O/'sources/drum_foreground_occlusion.png',fore)
for a in m['assets']:
 if a['path']==str(fore.relative_to(R)):a['sha256']=hashlib.sha256(fore.read_bytes()).hexdigest()
inv['version']+=1;inv['scope']='Luna full measures1-148; 10 static pairs, 8 live pairs; remaining20 pairs';iP.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n');mP.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(O/'ledger/motion_matrix.json').write_text(json.dumps(mat,ensure_ascii=False,indent=2)+'\n');(O/'qa/lt_promote_mapping.json').write_text(json.dumps(mapping,indent=2))
q={'status':'STATIC_VISUAL_PASS_LIVE_PENDING','keys':['LT:R','LT+SN:R/L'],'hit_tip':[885,416],'rebound_tip':[909,381],'hit_grip':[1008,480],'anatomy':'Far shoulder/upper arm/elbow inferred behind preserved hair/tom; rolled cuff to right clenched hand is continuous. Only right localized arm donor translated/rotated. Original left arm/head/body/stool/legs protected. Rebound wrist rotates18 degrees, tip clears visible head. Combo only swaps validated left-arm delta.','candidate_corrections':['Initial generated tip959319 missed LT; rigid transform corrected it to885416. Initial rebound sign moved tip down and was rejected; reversed to lift. Initial tip donor mask cut end, enlarged mask restores full tip.'],'foreground_update':'Head leans in front of left ride portion; hair/torso remain behind kit. Exact original drum pixels only.'};(O/'qa/lt_r_and_combo_v1.json').write_text(json.dumps(q,indent=2))
for sub in ['qa','scripts','ledger']:(P/sub).mkdir(exist_ok=True)
for f in ['qa/lt_r_and_combo_v1.json','qa/browser_post_promote_8_pairs.json','scripts/make_lt_r_pair.py','scripts/test_occlusion.py','scripts/promote_lt_r.py','ledger/motion_matrix.json']:shutil.copyfile(O/f,P/f)
resume=R/'character-assets/production/WORK_RESUME_20261008.md';s=resume.read_text().replace('8ペア16枚:', '10ペア20枚:').replace('RD:R、RD+SN:R/L。最初の4ペア8位相は公開Webでも検証済み。残り22ペア。RC/RDと新しい前後合成は公開検証待ち。','RD:R、RD+SN:R/L、LT:R、LT+SN:R/L。最初の8ペア16位相は公開Webで検証済み。残り20ペア。LT2ペアと頭部前後修正は公開検証待ち。').replace('LT:Rの局所腕生成が進行中。scratchに結果がなければcanonical Neutralと固定原画から再生成。','LT:R局所Hit/Reboundは合格し正式画像へ反映。HT:LとBD:RFの局所生成が進行中。').replace('残22ペア','残20ペア');s+='\n## 今回の公開実測\n9f45a995ca168da0fce884b46e80b064f7ee9f69 / r4: 8ペア16位相すべて正しいキー・位相・新PNG読み込み・前景canvasフレーム一致。Runtime Character QA、Character asset validation、deploy-siteはGitHub Actions SUCCESS。QA JSONは20261008/qa/browser_post_promote_8_pairs.json。新しい頭部mask修正後は再確認する。\n';resume.write_text(s)
for f in ['site/character-prototype.js','site/app.js','site/index.html']:
 p=R/f;p.write_text(p.read_text().replace('20261008-occlusion-r4','20261008-lt-r5'))
print(mapping)
