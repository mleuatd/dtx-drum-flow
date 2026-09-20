# 008 BD:RF hit — AI完全新規生成試作 v1

## 目的

既存008 PNGの消去・描き足し・合成を一切行わず、`generation-spec/` の文章仕様だけから人物差分を一から生成する方式を検証する。

## 分離方針

- 現在の正式runtime `character-assets/layers/character/bd/hit_rf.png` は変更しない。
- 本ディレクトリは完全新規生成方式専用の独立作業場所とする。
- ユーザー確認とQA合格前にruntimeへ昇格しない。

## 入力仕様

- `generation-spec/MASTER_GENERATION_SPEC.md`
- `generation-spec/CHARACTER_LOCK.json`
- `generation-spec/CAMERA_LOCK.json`
- `generation-spec/NEGATIVE_CONSTRAINTS.json`
- `generation-spec/actions/BD_RF.json`
- `generation-spec/frames/008_bd_rf_hit.json`

元008画像および他の人物PNGは生成入力・参照画像として使用していない。

## 出力

- `008_bd_rf_hit_from_scratch_v1.png`
- 1448×1086 PNG
- SHA-256: `88b2a98d508f0e8e0cf3044e13d90419e6f59e6fe8cdf791fc9d73e9c7b75522`

## 原寸視覚QA

### PASS

- 人物は1人
- 腕2本
- 手2つ
- 脚2本
- ブーツ2つ
- スティック2本、各手1本
- 第3脚・余分な腕・浮遊パーツなし
- 矩形合成痕なし
- 腰、スカート、脚、椅子の連続性は自然
- 白黒ラフ線画、長髪、チェック柄ジャケット、短スカート、ショートブーツ

### FAIL / 要修正

- 顔が画面右側に見え、`CAMERA_LOCK` の「顔は画面左に少し」と逆
- 指定の背後左回りカメラではなく、左右反転に近い
- BD:RF hitとして右足の踏み込みが弱く、打撃瞬間が明瞭でない
- 既存キャラクターより頭身・顔の見え方がやや大人寄り

## 判定

`HOLD_CANDIDATE_V1`

新規生成方式そのものは第3脚・矩形スプライス回避に有効。ただしカメラ方向とBD hit動作を強く固定したv2が必要。
