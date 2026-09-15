# Precision Audio Pipeline

DTX Drum Flow の高精度ドラム解析用パイプラインです。

## 目的

フルミックスから直接ひとつの Audio-to-MIDI モデルだけを使うのではなく、複数経路の結果を突き合わせて打点時刻を詰めます。

1. フルミックス → Demucs で drums / bass / other / vocals
2. drums stem → drumsep で kick / snare / hihat / cymbals / toms
3. 各 stem → librosa onset detector で候補時刻
4. フルミックスそのもの → transient/onset 候補
5. 任意で ADTOF Plus / MDX23C 系の MIDI も読み込む
6. 各候補を ±30〜60ms 程度でクラスタリング
7. 元音源のアタック、BPMグリッド、複数経路の一致数でスコアリング
8. 最終ノーツを JSON / MIDI に出力

## 重要

このディレクトリは Demucs / drumsep / MDX23C / ADTOF のコードや重みを同梱しません。
インストール済みの外部ツールを subprocess で呼ぶラッパーです。

### ライセンス

- Demucs: MIT
- drumsep: MIT
- ADTOF original: CC BY-NC-SA 4.0
- ADTOF Plus / ADTOF-pytorch / MDX23C wrappers: 各 upstream の LICENSE を必ず確認

商用利用を想定する場合は、ADTOF 原版の非商用条件を避ける構成を選んでください。

## 基本インストール

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r tools/audio_pipeline/requirements.txt
```

高精度構成では追加で:

```bash
pip install demucs
pip install drumsep
```

ADTOF Plus / MDX23C は upstream の手順で別途導入します。

## 実行

```bash
python tools/audio_pipeline/pipeline.py song.wav -o output
```

Demucs / drumsep が入っていれば自動利用します。なければフルミックスの onset 検出だけで動きます。

外部 MIDI を追加して多数決に参加させる場合:

```bash
python tools/audio_pipeline/pipeline.py song.wav -o output --midi candidate1.mid candidate2.mid
```

BPM が分かっている場合:

```bash
python tools/audio_pipeline/pipeline.py song.wav -o output --bpm 174
```

## 出力

- `notes.json` 最終ノーツ
- `drums.mid` GM channel 10 の MIDI
- `diagnostics.json` 各ノーツの信頼度・採用根拠
- `stems/` 利用できた場合の中間 stem

## 設計方針

- 一系統の誤検出をそのまま採用しない
- 近い時刻の候補をクラスタリングして合意数を取る
- kick / snare / hihat / cymbal / tom の帯域・stem情報を保持
- 元音源の transient に最終スナップ
- 低信頼ノーツには confidence を付ける
- ブラウザ側はこの JSON を読み込めるようにする予定
