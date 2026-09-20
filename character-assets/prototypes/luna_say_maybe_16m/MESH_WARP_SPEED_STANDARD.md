# 008成功方式 高速化・標準化 v1

## 目的

008で成立した topology-preserving mesh warp を、品質を落とさず再利用できる標準工程にする。高速化対象は準備、候補生成、QA、固定ドラム確認画像生成、GitHub登録までであり、原寸視覚QAやユーザー確認は省略しない。

## 基準

- 基準コミット: `701821d17aa09bc5c46b6e39cc7c811cacf9fff6`
- 代表対象: `008_bd_rf_hit.png`
- 成功候補: `character-assets/generation-trials/mesh-warp-008-v1/008_bd_rf_hit_mesh_v1_review.png`
- 設定: `character-assets/generation-trials/mesh-warp-008-v1/008_mesh_config.json`
- 標準プロファイル: `character-assets/config/mesh_warp_fast_lossless_v1.json`

## 品質を落とさない高速化

PNGは引き続き可逆。従来の `optimize=True` を標準経路から外し、`compress_level=1` を使う。これはPNGの圧縮時間とファイルサイズのトレードオフだけを変更し、デコード後のRGBA画素値は変更しない。

固定ドラム確認画像では、候補PNGを一度保存してから再度読み込む処理を廃止する。変形直後のRGBA配列をそのまま合成へ渡す。これにより候補の再読込を削減する。

候補、QA、固定ドラム確認画像、timingを1プロセスで生成する。ツールや画像の再取得を候補ごとに繰り返さない。

## 標準コマンド

```bash
python3 tools/character_layers/build_mesh_warp_pose.py \
  --config character-assets/generation-trials/mesh-warp-008-v1/008_mesh_config.json \
  --source character-assets/layers/character/bd/rebound_rf.png \
  --output character-assets/generation-trials/mesh-warp-008-v1/008_bd_rf_hit_mesh_v1.png \
  --fixed-drum character-assets/layers/drums/drum_base.png \
  --preview-output character-assets/generation-trials/mesh-warp-008-v1/008_bd_rf_hit_fixed_drum_v1.png \
  --qa-output character-assets/generation-trials/mesh-warp-008-v1/008_qa.json \
  --timing-output character-assets/generation-trials/mesh-warp-008-v1/008_timing.json \
  --png-compress-level 1
```

## 既存008実測（変更前ベースライン）

既存の `008_timing.json` から:

- load: 0.042191 s
- warp: 0.056988 s
- candidate save: 0.437810 s
- QA: 0.042731 s
- fixed drum composite/save: 1.190685 s
- total: 1.770454 s

変形計算そのものは約0.057秒で、全体の約96%はそれ以外、特にPNG書き出し側にあった。したがって今回の高速化は変形アルゴリズムや補間品質を触らず、可逆PNG保存と再読込のオーバーヘッドを削る。

## 再計測ルール

変更後の実測は同じ008設定・同じsource・同じfixed drumで行い、`008_timing.json` を更新する。比較時は必ずQAの以下が一致することを確認する。

- canvas 1448x1086
- outsideAllowedChangedPixels = 0
- changedPixels
- changedBBox
- pedalDistancePx
- machinePass = true
- 原寸視覚QAの見た目

PNGファイルのSHAは圧縮方式変更により変わり得るため、品質同一性はデコード後RGBA画素比較で確認する。

## 横展開

008の標準化確認後のみ、010 -> 014 -> 028 -> 032 の順に同方式へ展開する。各画像ごとにROI・ランドマークJSONだけを差し替え、ツール本体は共通化する。
