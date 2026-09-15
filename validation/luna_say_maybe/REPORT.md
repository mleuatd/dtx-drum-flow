# Luna say maybe 実音源検証 — 2026-09-15

## 使用した実ファイル

Library に残っていた元音源:
- `a5bdd1d6-8c30-4143-bbd4-3603c4b83dfb.mp3`
- 約 266.945 秒
- 44.1 kHz stereo MP3

以前生成した比較対象:
- `Luna_say_maybe_drums_only.mp3`
- `Luna_say_maybe_drums.mid`
- 旧 MIDI: 2,236 notes

## 元音源からの再解析

librosa の beat tracker では推定 BPM は約 **139.675**。
過去作業で使っていた BPM 139 と大きく矛盾しない。

旧 MIDI をそのまま正解とはせず、元音源から以下の帯域別 spectral-flux evidence を作った。

- kick: 30–180 Hz
- toms: 100–700 Hz
- snare: 500–6000 Hz
- hihat: 5000–11000 Hz
- cymbals: 3500–11000 Hz

各パートごとに ±250 ms の範囲で全体オフセットを探索し、その後 ±90 ms の局所窓で元音源 transient を探索した。

## 実測結果

| family | notes | global offset | snap | low confidence |
|---|---:|---:|---:|---:|
| kick | 533 | -8 ms | 95.5% | 5.3% |
| snare | 856 | -14 ms | 43.0% | 59.8% |
| toms | 137 | -14 ms | 49.6% | 53.3% |
| hihat | 413 | -8 ms | 56.7% | 45.5% |
| cymbals | 297 | -10 ms | 53.9% | 53.2% |

## 判定

旧 MIDI は、**キックの時刻はかなり元音源と整合している**。

一方で snare / toms / hihat / cymbals は、元音源上の対応 transient evidence が弱いノーツが多数ある。
これは単純な数 ms の時間ズレだけでは説明できず、以下が混在している可能性が高い。

- パート誤分類
- 過剰検出
- guitar / other transient の誤認
- cymbal sustain を複数打点として扱う誤り
- tom / snare の取り違え
- high-frequency transient の hihat/cymbal 取り違え

したがって、旧 MIDI を一括オフセット補正するだけで完成とはしない。

## 低信頼ノーツが多い区間

10 秒単位では特に以下が悪かった。

- 60–70 s
- 120–130 s
- 140–150 s
- 170–180 s
- 190–210 s
- 220–250 s

ここは次段階のモデル比較・再転写時に重点確認する。

## Demucs 再分離について

この通常チャット環境には Demucs 本体は導入済みだったが、htdemucs の学習済み重みがローカルキャッシュに無く、実行時の重みダウンロードがネットワーク制限で失敗した。

そのため、今回の検証は
- 元音源本体
- 旧 drums-only 音源
- 旧 MIDI
- 元音源の帯域別 transient evidence

を直接利用して行った。

Demucs model weight が利用可能な Work 環境では、本レポートの低信頼区間を優先して再分離・再転写すること。

## 実装反映

実曲検証で有効だった処理を汎用化して
`tools/audio_pipeline/realign_existing_midi.py`
として追加する。

ブラウザ側は precision JSON 内の `part` を優先して読み込み、confidence を色・透明度に反映する。
