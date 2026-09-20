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
  --timing-output character-assets/generation-trials/mesh-warp-008-v1/008_timing.json
```

## 実測と判定

- 合計: 1.77秒
- warp本体: 0.057秒
- 変更画素: QA JSON参照
- 対象外変更: 0画素
- ペダル目標許容内: PASS
- 人体連続性・柄・見た目: 原寸目視が必要

`*_review.png` はGitHub上で直接確認しやすい256色レビュー用PNGで、寸法は原寸1448×1086。正式候補は再生成コマンドで得る。

## 高速化メモ

初回だけ入力を取得する。以後はJSONの制御点だけ調整して約2秒で候補・QA・ドラム合成を同時更新する。品質維持のため、ROI解像度、補間次数、原寸確認は削らない。
