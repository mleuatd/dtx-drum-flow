# 精度評価

正解となるドラムMIDIがある場合、解析結果のタイミング精度を数値化できます。

```bash
python tools/audio_pipeline/evaluate.py output/notes.json reference.mid -o evaluation.json
```

以下を ±25ms / ±50ms / ±100ms で出します。

- Precision
- Recall
- F1
- 平均絶対時間誤差
- 95パーセンタイル時間誤差
- kick / snare / hihat / toms / cymbals ごとのF1

特に本プロジェクトでは **±25ms の F1 と時間誤差**を主要指標にします。
