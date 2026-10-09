"""Promote visually reviewed triplet; immutable outside local masks."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
R=next(p for p in Path(__file__).resolve().parents if (p/'character-assets').is_dir())
P=R/'character-assets/production/20261009';Q=P/'qa';C=P/'candidates';B=P/'baseline'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
review=json.loads((Q/'visible_review.json').read_text());assert review['status']=='PASS'
report=json.loads((Q/'candidate_report.json').read_text())
oldkit=np.array(Image.open(B/'drum_base_before.png').convert('RGBA'));newkit=np.array(Image.open(C/'drum_base_candidate.png').convert('RGBA'))
allowed=np.array(Image.open(Q/'drum_change_mask.png'))>0
assert np.array_equal(oldkit[~allowed],newkit[~allowed])
roi=np.zeros(oldkit.shape[:2],bool);roi[730:1005,560:800]=True
templates={phase:np.array(Image.open(C/f'{phase}_candidate.png').convert('RGBA')) for phase in ['hit','rebound','ready']}
ip=R/'character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json';inv=json.loads(ip.read_text())
mp=R/'character-assets/config/assets_manifest.json';manifest=json.loads(mp.read_text())
changed={};records=[]
for key in inv['runtimeQaTarget']['actions']:
    for phase in ['hit','rebound']:
        frame=inv['requiredFrames'][inv['runtimePhaseFrameMap'][key][phase]];path=R/'character-assets'/frame['path']
        old=np.array(Image.open(path).convert('RGBA'));new=old.copy()
        template=templates['hit' if key.startswith('BD') and phase=='hit' else 'ready'];new[roi]=template[roi]
        assert np.array_equal(old[~roi],new[~roi])
        # The entire near-left leg remains byte-identical, including inside ROI.
        left=np.zeros(old.shape[:2],bool);left[800:1005,560:620]=True
        assert np.array_equal(old[left],new[left])
        Image.fromarray(new).save(path);s=sha(path);changed[str(path.relative_to(R))]=s
        frame.update(sha256=s,qaStatus='VISIBLE_LOCAL_PEDAL_LEG_PASS_RUNTIME_PENDING')
        records.append({'key':key,'phase':phase,'path':str(path.relative_to(R)),'sha256':s,'outsideFootRoiExact':True,'nearLeftLegProtected':True})
assert len(records)==60 and len(changed)==60
neutral=R/'character-assets/layers/character/base/neutral_performance_ready.png'
shutil.copy(C/'ready_candidate.png',neutral);changed[str(neutral.relative_to(R))]=sha(neutral)
inv['requiredFrames']['neutral'].update(sha256=sha(neutral),qaStatus='VISIBLE_LOCAL_PEDAL_LEG_PASS_RUNTIME_PENDING')
drum=R/'character-assets/layers/drum/drum_base.png';shutil.copy(C/'drum_base_candidate.png',drum);newsha=sha(drum);changed[str(drum.relative_to(R))]=newsha
manifest['previousLockedDrumSha25620261008']=manifest['lockedDrumSha256'];manifest['lockedDrumSha256']=newsha
manifest['drumRevision20261009']={'authorization':'User expressly permits pedal and minimal connection repairs only','baselineBranch':'checkpoints/2026-10-09-before-pedal-leg-alignment','baselinePath':str((B/'drum_base_before.png').relative_to(R)),'changeMask':str((Q/'drum_change_mask.png').relative_to(R)),'outsideMaskPixelExact':True,'visibleDrumLayers':1}
for asset in manifest['assets']:
    if asset['path'] in changed:
        asset['sha256']=changed[asset['path']]
        asset.setdefault('notes',[]).append('20261009 authorized pedal/right-leg local repair: visible triplet PASS; exact outside masks; public QA pending.')
        if asset['path'].endswith('/drum_base.png'):asset['purpose']='fixed single-layer drum after authorized pedal-only revision'
inv['qa']['fixedDrumSha256']=newsha;inv['qa']['fixedDrumPixelSha256']=hashlib.sha256(newkit.tobytes()).hexdigest()
inv['production20261008']['pedalLegRevision20261009']='VISIBLE_PASS_PUBLIC_PENDING'
inv['runtimeQaTarget'].update(progressPath='character-assets/production/20261009/qa/public_runtime.json',blockKey='LUNA_PEDAL_ALIGNMENT_20261009',requestedAt='2026-10-09')
write(ip,inv);write(mp,manifest)
lp=R/'character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json';ledger=json.loads(lp.read_text());ledger['drum']['sha256']=newsha
for target in ledger['targets']:
    if target.get('formalGitHubPath') in changed:
        target.update(sha256=changed[target['formalGitHubPath']],qaState='PEDAL_LEG_VISIBLE_PASS_RUNTIME_PENDING',pedalLegRevision20261009='VISIBLE_PASS_RUNTIME_PENDING')
write(lp,ledger)
mm=P.parent/'20261008/ledger/motion_matrix.json';motion=json.loads(mm.read_text())
for action in motion['actions']:action['pedalLegRevision20261009']='VISIBLE_PASS_RUNTIME_PENDING'
write(mm,motion)
restore=R/'character-assets/production/20261008/scripts/restore_source_workspace.py'
s=restore.read_text().replace(manifest['previousLockedDrumSha25620261008'],newsha);restore.write_text(s)
for name in ['site/character-prototype.js','site/app.js','site/index.html']:
    f=R/name;s=f.read_text().replace('20261008-foot-continuity-r12','20261009-pedal-leg-r1').replace('20261009-hud-fix-r1','20261009-pedal-leg-r1');f.write_text(s)
report.update(status='PROMOTED_VISIBLE_PASS_PUBLIC_RUNTIME_PENDING',newFixedDrumSha256=newsha,previousFixedDrumSha256=sha(B/'drum_base_before.png'),frames=records)
write(Q/'promotion_report.json',report)
write(Q/'public_runtime.json',{'status':'PUBLIC_RUNTIME_PENDING','revision':'pedal-leg-20261009','blocker':None})
write(P/'checkpoint.json',{'status':'PROMOTED_VISIBLE_PASS_PUBLIC_RUNTIME_PENDING','baselineSha':'33e17e37fd235ad474b61219e664670d9818c344','baselineBranch':'checkpoints/2026-10-09-before-pedal-leg-alignment','next':'Trigger deploy/public Runtime Character QA with all30 targets; require single visible drum and public source SHA match; save report/screenshots then mark complete.'})
resume=R/'character-assets/production/WORK_RESUME_20261008.md'
s=resume.read_text();s='> 最新状態: 2026-10-09 右脚＋ペダルの局所修正を反映済み。公開再検証待ち。過去の完了報告は旧版の記録です。\n\n'+s
s+='\n### 右脚＋ペダル修正版の昇格\n待機・Hit・Reboundの可視人体と接触を確認PASS。正式60枚と待機、ペダルを統合したドラム1枚へ反映。20261009/qa/promotion_report.jsonに旧/新SHAと全60枚の範囲外一致を保存。公開再検証は20261009/qa/public_runtime.jsonへ記録します。\n';resume.write_text(s)
print(json.dumps({'status':report['status'],'frames':len(records),'newFixedDrumSha256':newsha,'outsideDrumMaskExact':True,'all60OutsideFootRoiExact':True}))
