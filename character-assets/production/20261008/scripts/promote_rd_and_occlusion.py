from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
O=Path('work_output');R=Path('repo'); prod=R/'character-assets/production/20261008'
lh=np.array(Image.open(O/'variants/sn/hit_l_candidate_v3.png'));lr=np.array(Image.open(O/'variants/sn/rebound_l_candidate_v3.png'));delta=np.any(lh!=lr,axis=2)
(O/'variants/combo').mkdir(exist_ok=True)
for phase in ['hit','rebound']:
 a=np.array(Image.open(O/f'variants/rd/{phase}_r_local_v2.png'))
 if phase=='rebound':a[delta]=lr[delta]
 Image.fromarray(a).save(O/f'variants/combo/rd_sn_r_l_{phase}_v1.png')
invp=R/'character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json';inv=json.loads(invp.read_text());mp=R/'character-assets/config/assets_manifest.json';m=json.loads(mp.read_text());matrix=json.loads((O/'ledger/motion_matrix.json').read_text());mapping={}
for key in ['RD:R','RD+SN:R/L']:
 for phase in ['hit','rebound']:
  frameid=inv['runtimePhaseFrameMap'][key][phase];entry=inv['requiredFrames'][frameid];target=R/'character-assets'/entry['path'];src=O/(f'variants/rd/{phase}_r_local_v2.png' if key=='RD:R' else f'variants/combo/rd_sn_r_l_{phase}_v1.png');shutil.copyfile(src,target);sha=hashlib.sha256(target.read_bytes()).hexdigest();entry.update(sha256=sha,state='ready',qaStatus='STATIC_VISUAL_PASS_LIVE_PENDING');mapping[str(target.relative_to(R))]=str(src)
  for asset in m['assets']:
   if asset['path']==str(target.relative_to(R)):asset.update(sha256=sha,status='SOURCE_BOUND_STATIC_QA_PASS',notes=['20261008 source-bound RD pair; live QA pending'])
 for a in matrix['actions']:
  if a['runtime_key']==key:a.update(status='STATIC_QA_PASSED_LIVE_PENDING',new_hit='variants/rd/hit_r_local_v2.png' if key=='RD:R' else 'variants/combo/rd_sn_r_l_hit_v1.png',new_rebound='variants/rd/rebound_r_local_v2.png' if key=='RD:R' else 'variants/combo/rd_sn_r_l_rebound_v1.png')
inv['version']+=1; inv['scope']='Luna full chart measures 1-148; 8 source-bound pairs static passed, 4 pairs live verified';invp.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n');mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');(O/'ledger/motion_matrix.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n');(O/'qa/rd_promote_mapping.json').write_text(json.dumps(mapping,indent=2))
fixed=np.array(Image.open(O/'sources/drum_fixed.png').convert('RGBA'));fore=np.array(Image.open(O/'sources/drum_foreground_occlusion.png').convert('RGBA'));mask=fore[:,:,3]>0
q={'status':'PIXEL_PROVENANCE_PASS_RENDER_PENDING','foreground_selected_pixel_mismatches':int(np.count_nonzero(np.any(fixed[mask]!=fore[mask],axis=1))),'original_drum_sha256':hashlib.sha256((O/'sources/drum_fixed.png').read_bytes()).hexdigest(),'foreground_file_sha256':hashlib.sha256((O/'sources/drum_foreground_occlusion.png').read_bytes()).hexdigest(),'draw_order':['original fixed drum','complete original-pose character','verbatim selected drum pixels','same character arm pixels only','effects'],'note':'No drum line is edited. Torso/hair behind selected drums; validated moving arms/sticks in front. Browser performance/visual verification pending.'}
(O/'qa/occlusion_provenance.json').write_text(json.dumps(q,indent=2))
for sub in ['qa','scripts','ledger']:(prod/sub).mkdir(parents=True,exist_ok=True)
for f in ['qa/rd_r_local_v2.json','qa/occlusion_provenance.json','scripts/make_rd_pair.py','scripts/test_occlusion.py','scripts/promote_rd_and_occlusion.py','ledger/motion_matrix.json']:shutil.copyfile(O/f,prod/f)
p=R/'character-assets/production/WORK_RESUME_20261008.md'
p.write_text('''# 作業再開入口 — 2026-10-08\n\n**全作業は未完了です。** 目標はLuna全30動作60枚を自然な人体・固定ドラムで完成し公開Webで検証することです。\n\n## 現在の状態\n- 30動作60位相の既存Web切替と画像読み込みを実測済み。描画成功と絵の合格は別です。\n- 新しい静的QA合格は8ペア16枚: SN:L、SN:R、HH:R、HH+SN:R/L、RC:R、RC+SN:R/L、RD:R、RD+SN:R/L。最初の4ペア8位相は公開Webでも検証済み。残り22ペア。RC/RDと新しい前後合成は公開検証待ち。\n- 固定ドラムと承認NeutralのSHAは不変。髪・胴・脚・近い腕を保護し、必要な腕だけ局所編集。全身AI出力は完成画像として採用しない。\n- 413過去画像の一覧と分類: 20261008/ledger/image_audit.json。個別拡大未完了の判定保留を成功donorとして使わない。\n- RDの最初のAI生成は打点が高すぎて不合格。元Neutralの手とスティックを局所変形したv2を使用。HT:L試作は袖の白い切れと残像で不合格。\n- ドラム原画の一部RGBAをそのまま複製した前景PNGと腕前景canvasで、髪/身体をタム・ライドの後ろに置く合成処理を追加。原画改変ではない。公開Webの見た目・性能の検証は次の作業。\n\n## 保存場所\n入口: character-assets/production/WORK_RESUME_20261008.md\n詳細: character-assets/production/20261008/{ledger,qa,scripts,donors}/\n正式画像: character-assets/layers/character/ 各楽器とcombo。\n入力: DTX_Drum_Flow_Work_素材一式と制作仕様書_20261008.zip、libfile_cb32a71ec6688191b3cd32ae3785f0b9。指定名WORK_MASTER_SPEC_REVISED.mdはZIPになく、同梱WORK_MASTER_SPEC.mdとユーザー1〜10を適用。\n\n## 再開手順\n1. 最新mainとこの入口、ledger/motion_matrix.jsonを読む。公開サイトのcache version 20261008-occlusion-r4 と前景レイヤーを確認。8ペア16位相を実測し、人体と打点も画面で確認。\n2. LT:Rの局所腕生成が進行中。scratchに結果がなければcanonical Neutralと固定原画から再生成。赤いガイドは参考だけで完成画像に含めない。LT打面は885,416付近、旧885,455は側面。\n3. HT左右、LT左右、FT左右、BD右足を制作し、合格部位だけ組み合わせて残22ペアを制作。BD旧735,650はドラム面で足の打点ではない。実際のペダル板を使用。\n4. 各ペアで人体・同一人物・Hit接触・Rebound離隔・固定部分を検査し、不合格は修正。GitHubに実体・台帳・失敗理由・次位置を保存する。\n5. 公開Webの全30動作60位相と再生、PC/モバイルを検証。画像の合格と読み込みの合格を区別する。\n\n## 確定したチェック\ncommit41635d06b706d8e399821f9ff80b369c87c3bc19のvalidateとRuntime Pose SN-L Source QAはGitHub Actions SUCCESS。以後の変更は改めて確認。画像の独立したReboundを使うようSN:R設定を修正済み。\n''')
print(mapping,q)
