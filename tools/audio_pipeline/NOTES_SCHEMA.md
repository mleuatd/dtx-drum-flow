# notes.json schema

```json
{
  "bpm": 120.0,
  "notes": [
    {
      "time": 1.234,
      "kind": "snare",
      "velocity": 104,
      "confidence": 0.88,
      "votes": 3,
      "sources": ["demucs-drums", "drumsep-snare", "midi-1"]
    }
  ]
}
```

`kind` is one of `kick`, `snare`, `hihat`, `toms`, `cymbals`, `unknown`.

ブラウザ側では kind を既存レーンへ割り当てます。
