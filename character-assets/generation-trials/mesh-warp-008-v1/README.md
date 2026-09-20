# 008 BD:RF hit メッシュ変形候補 v1

## 状態

`REVIEW_REQUIRED`。runtime未反映。他画像への横展開禁止。008のユーザー承認前に010／014／028／032その他へ適用しない。

## 目的

監査PASS済み `rebound_rf.png` を土台に、右脚・ブーツ・alphaを一体で連続変形し、BD右足hitのペダル位置へ寄せる。新規描画、矩形貼付け、別画像からの脚移植は行わない。

## 標準1コマンド

```bash
python3 tools/character_layers/run_visual_repair_trial.py \
  --frame-config character-assets/generation-trials/mesh-warp-008-v1/008_mesh_config.json \
  --source character-assets/layers/character/bd/rebound_rf.png \
  --broken-source character-assets/layers/character/bd/hit_rf.png \
  --fixed-drum character-assets/layers/drum/drum_base.png \
  --output-dir character-assets/generation-trials/mesh-warp-008-v1
```

この1コマンドで、入力SHA確認、SHAベースキャッシュ、設定検証、原寸RGBA候補生成、機械QA、固定ドラム合成、修復前後比較、軽量確認画像、実測時間、実行マニフェスト、GitHub登録候補一覧まで生成する。

一時キャッシュは `.cache/visual-repair/` に置きGit管理しない。各入力の元パス、SHA-256、cache hit/miss は `008_run_manifest.json` に残す。SHAが同じ限り再取得・再コピーしない。

## 正式候補と確認用画像

- 正式候補: `008_bd_rf_hit_mesh_v1.png`
  - 1448×1086
  - RGBA
  - lossless PNG
  - 透明背景
- 単体確認用: `008_bd_rf_hit_mesh_v1_review.webp`
- 固定ドラム合成確認用: `008_bd_rf_hit_fixed_drum_v1_review.webp`
- 修復前後確認用: `008_before_after_review.webp`

`*_review.webp` は確認専用であり、正式候補とは別物。確認用画像の圧縮・表示上の問題を正式候補の破損と混同しない。

## QA

`008_qa.json` で最低限次を自動検査する。

- 1448×1086
- RGBA / alpha channel
- 候補が入力と完全同一でない
- 許可領域外変更 0画素
- 固定領域変更 0画素
- 変更bbox
- ペダル打点距離と許容距離
- source / broken source / fixed drum / config / candidate のSHA-256
- 既存008成功値との回帰一致
- runtime反映禁止状態
- user approval未完了状態

`machinePass=true` でも `visualQaRequired=true` を維持する。人体の自然さ、脚の本数、柄、関節の連続性はユーザー原寸目視の対象であり、機械PASSだけでruntimeへ反映しない。

## 実測

変更前ベースライン:

- 合計: 1.770454秒
- warp本体: 0.056988秒
- candidate save: 0.437810秒
- fixed drum composite/save: 1.190685秒

高速化後の実測値は同じ008を実行して `008_timing.json` と `008_regression_run.json` に保存する。速度向上のためにROI解像度、補間、原寸解像度、QA項目を削らない。

## GitHub登録安全条件

- machine QA FAIL時は正式候補を登録対象へ入れない。
- `character-assets/layers/character/` 配下runtimeを登録対象に含めない。
- 010／014／028／032その他の対象外frameを含めない。
- force pushしない。
- main先頭が作業開始時から変わった場合は、そのままref更新せず最新mainに追従して差分を再構成する。
- 008ユーザー承認まで正式runtimeを上書きしない。

詳細: `character-assets/prototypes/luna_say_maybe_16m/MESH_WARP_SPEED_STANDARD.md`


## 008回帰試験結果（2026-09-21）

- machinePass: true
- formal candidate: 1448×1086 RGBA
- changedPixels: 36,721
- changedBBox: x=594, y=635, width=172, height=326
- 許可領域外変更: 0画素
- 固定領域変更: 0画素
- ペダル距離: 11.18px / 許容45px
- candidate SHA-256: `4ee11bd49363502e2536bf3a2dce3a1b1f1bd873721d32af7eb667dfe9a93caf`
- 候補生成から確認用成果物完成: 1.952556秒
- ラッパー全体: 2.027783秒
- CI内回帰呼出し全体: 2.645649秒
- runtimeModified: false
- otherFramesTouched: false
- userApprovalStatus: PENDING
- visualQaRequired: true
