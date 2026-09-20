# 008成功方式 高速化・標準化 v2

## 目的

008で成立した topology-preserving mesh warp を、品質を落とさず高速に再利用できる標準工程にする。高速化対象は入力準備、候補生成、QA、確認画像生成、GitHub登録であり、原寸視覚QAやユーザー確認は省略しない。

## 基準

- 基準コミット: `701821d17aa09bc5c46b6e39cc7c811cacf9fff6`
- 代表対象: `008_bd_rf_hit.png`
- 成功候補: `character-assets/generation-trials/mesh-warp-008-v1/008_bd_rf_hit_mesh_v1_review.png`
- 設定: `character-assets/generation-trials/mesh-warp-008-v1/008_mesh_config.json`
- 標準プロファイル: `character-assets/config/mesh_warp_fast_lossless_v1.json`
- 共通変形本体: `tools/character_layers/build_mesh_warp_pose.py`
- 標準ラッパー: `tools/character_layers/run_visual_repair_trial.py`

## 品質不変条件

- formal candidateは1448×1086 RGBA lossless PNG。
- warp interpolation order、ROI、制御点、変形場は008成功設定を維持する。
- 身体輪郭、衣服、柄、ブーツ、alphaを同じ変形場で処理する。
- 顔、髪、腕、左脚、椅子、固定ドラムは変形しない。
- 許可領域外変更0、固定領域変更0を機械QAで要求する。
- `visualQaRequired=true` を常に維持する。
- machine PASSだけでruntimeへ昇格しない。

PNGの `compress_level=1` は可逆圧縮の計算量だけを下げる。デコード後RGBA画素値は圧縮レベルに依存しない。固定ドラム確認画像は変形直後のRGBA配列から直接合成し、候補PNGの再読込を行わない。

## 入力キャッシュ

ラッパーは各入力をSHA-256で識別し、既定では `.cache/visual-repair/` にキャッシュする。

対象:
- 正常土台PNG
- 修復前PNG
- 固定ドラムPNG
- frame config

同じSHAのファイルは再コピーしない。SHAが変わった時だけ新しいcache entryを作る。キャッシュ本体はGitHubへ保存しない。

`008_run_manifest.json` に元パス、SHA-256、cache hit/missを記録する。

## 設定テンプレート

008 JSONは既存 `sourcePoints` / `targetPoints` 等との互換性を維持しつつ、次を自己記述する。

- actionKey / phase / frameId
- inputPng / normalSourcePng / fixedDrumPng
- outputDir
- ROI
- deformationPolygon / fixedRects
- hip / knee / ankle / toe / pedalEndpoint / pedalTarget
- sourcePoints / targetPoints
- pedalTolerancePx
- normalSourceSha256 / brokenSourceSha256 / fixedDrumSha256
- runtimeWritable
- userApprovalStatus
- visualQaRequired
- expectedRegression

同型修復ではツール本体を書き換えずJSON座標だけ変更する。ただし008のユーザー承認前は他frameへ横展開しない。

## 標準1コマンド

```bash
python3 tools/character_layers/run_visual_repair_trial.py \
  --frame-config character-assets/generation-trials/mesh-warp-008-v1/008_mesh_config.json \
  --source character-assets/layers/character/bd/rebound_rf.png \
  --broken-source character-assets/layers/character/bd/hit_rf.png \
  --fixed-drum character-assets/layers/drum/drum_base.png \
  --output-dir character-assets/generation-trials/mesh-warp-008-v1
```

処理順:
1. input SHA確認・cache判定
2. config検証
3. 1448×1086 RGBA candidate生成
4. machine QA
5. fixed drum合成
6. formal candidateとは別の軽量review生成
7. before/after review生成
8. timing記録
9. run manifest生成
10. commit manifest生成

## 機械QA

最低限:
- canvas 1448×1086
- RGBA / alpha channel
- candidate != source
- outside allowed changed pixels = 0
- fixed region changed pixels = 0
- changed bbox
- pedal endpoint distance <= tolerance
- input/config/output SHA-256
- expected 008 regression values
- runtimeWritable=false
- userApprovalStatus != APPROVED

FAIL時は候補をGitHub登録候補へ含めない。機械QAは原寸視覚QAを置き換えない。

## 正式候補と確認用の分離

- formal: `008_bd_rf_hit_mesh_v1.png`
- review: `008_bd_rf_hit_mesh_v1_review.webp`
- fixed drum review: `008_bd_rf_hit_fixed_drum_v1_review.webp`
- before/after review: `008_before_after_review.webp`

WebPは確認用のみ。正式候補はPNG RGBA原寸を維持する。

## GitHub登録

`008_commit_manifest.json` で登録対象と安全条件を記録する。ラッパーの `--git-commit --start-main-sha <sha>` は、origin/mainの先頭一致、runtime path不在、010／014／028／032不在を確認してからコミットする。

CI回帰も同じ制約を持ち、runtimeと対象外frameの差分を検出した場合は失敗させる。force pushは禁止。

最終main登録直前にもmain先頭を再確認する。途中更新があれば古い親へrefを強制更新せず、最新main上で安全に差分を再構成する。

## ベースラインと再計測

旧008:
- load: 0.042191 s
- warp: 0.056988 s
- candidate save: 0.437810 s
- QA: 0.042731 s
- fixed drum composite/save: 1.190685 s
- total: 1.770454 s

高速化後は `008_timing.json` に工程別実測を保存する。特に `candidateToReviewCompleteSeconds` を、候補生成からQA・固定ドラムreview・比較review完成までの実測として扱う。

品質回帰はファイル圧縮SHAの一致ではなく、同一warp設定の changedPixels、changedBBox、outsideAllowedChangedPixels、pedalDistance、原寸視覚QAで確認する。

## 横展開禁止

008のユーザー最終承認までは010／014／028／032その他へ適用しない。承認後にのみ各frame固有のJSONを作成し、共通ツールは変更せず横展開する。


## 008実回帰結果（2026-09-21）

同一設定による実回帰は machine PASS。正式候補は1448×1086 RGBAで、changedPixels=36,721、changedBBox=(594,635,172,326)、outsideAllowed=0、fixedRegionChanged=0、pedalDistance=11.18pxで既存成功値と一致した。

実測:
- cache/hash: 0.008024 s
- cached inputs load: 0.066825 s
- warp: 0.144989 s
- formal candidate save: 0.071159 s
- machine QA: 0.028261 s
- fixed drum review: 0.650539 s
- review images: 1.057608 s
- candidate -> review complete: 1.952556 s
- wrapper total: 2.027783 s
- CI regression invocation total: 2.645649 s

初回実行のためcacheHitはfalseだが、候補から確認成果物完成まで2秒弱で性能目標「数秒以内」を満たした。runtimeと他frameは未変更。ユーザー原寸目視は未完了なので `visualQaRequired=true` / `userApprovalStatus=PENDING` を維持する。
