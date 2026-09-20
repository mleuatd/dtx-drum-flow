# 008 BD:RF hit メッシュ変形候補 v1

## 状態

`REVIEW_REQUIRED`。runtime未反映。他画像への横展開禁止。

## 目的

監査PASS済み `rebound_rf.png` を土台に、右脚・ブーツ・alphaを一体で連続変形し、BD右足hitのペダル位置へ寄せる。新規描画、矩形貼付け、別画像からの脚移植は行わない。

## 再生成

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

## 実測と判定

変更前ベースライン:
- 合計: 1.770454秒
- warp本体: 0.056988秒
- candidate save: 0.437810秒
- fixed drum composite/save: 1.190685秒
- 変更画素・対象外変更・ペダル判定: QA JSON参照
- 人体連続性・柄・見た目: 原寸目視が必要

`*_review.png` はGitHub上で直接確認しやすいレビュー用PNG。正式候補は再生成コマンドで得る。

## 高速化標準

`tools/character_layers/build_mesh_warp_pose.py` は、品質を維持したまま保存待ちを減らすため、lossless PNG `compress_level=1` を標準にする。固定ドラム確認画像は変形直後のRGBA配列から直接合成し、候補PNGの再読込を行わない。

詳細: `character-assets/prototypes/luna_say_maybe_16m/MESH_WARP_SPEED_STANDARD.md`
