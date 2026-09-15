from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import mido

GM_TO_PART = {
    35:"BD", 36:"BD",
    37:"SN", 38:"SN", 39:"SN", 40:"SN",
    42:"HH", 44:"LP", 46:"HH",
    48:"HT", 50:"HT",
    45:"LT", 47:"LT",
    41:"FT", 43:"FT",
    49:"RC", 52:"RC", 55:"RC", 57:"RC",
    51:"RD", 53:"RD", 59:"RD",
}
PART_KIND = {
    "BD":"kick","SN":"snare","HH":"hihat","LP":"hihat",
    "HT":"toms","LT":"toms","FT":"toms",
    "RC":"cymbals","RD":"cymbals",
}
DTX_CHANNEL = {
    "HH":"11","SN":"12","BD":"13","HT":"14","LT":"15",
    "RC":"16","FT":"17","RD":"19","LP":"1A",
}


def extract_notes(songsterr_json: Path, offset: float):
    data = json.loads(songsterr_json.read_text(encoding="utf-8"))
    meta = data["meta"]
    tracks = meta.get("tracks", [])
    drum_index = next(
        (i for i,t in enumerate(tracks)
         if t.get("instrumentId") == 1024 or "drum" in str(t.get("instrument","")).lower()),
        None
    )
    if drum_index is None:
        raise RuntimeError("No drum track found")

    drum = data["parts"][drum_index]
    tempos = drum.get("automations", {}).get("tempo", []) or []
    bpm = float(tempos[0].get("bpm", 139)) if tempos else 139.0
    if any(float(t.get("bpm", bpm)) != bpm for t in tempos):
        raise RuntimeError("Tempo changes are not yet supported by this converter")

    sec_per_whole = (60.0 / bpm) * 4.0
    measure_start = 0.0
    measure_starts = []
    notes = []

    for mi, measure in enumerate(drum["measures"]):
        sig = measure.get("signature", [4,4])
        measure_len_whole = sig[0] / sig[1]
        measure_starts.append(measure_start)

        for vi, voice in enumerate(measure.get("voices", [])):
            cursor_whole = 0.0
            for bi, beat in enumerate(voice.get("beats", [])):
                if beat.get("graceNote"):
                    continue
                dur = beat.get("duration", [1,4])
                dur_whole = dur[0] / dur[1]
                t = measure_start + cursor_whole * sec_per_whole + offset
                for note in beat.get("notes", []):
                    if note.get("rest"):
                        continue
                    gm = int(note.get("fret", -1))
                    part = GM_TO_PART.get(gm)
                    if not part:
                        continue
                    notes.append({
                        "time": round(t, 6),
                        "part": part,
                        "gmNote": gm,
                        "kind": PART_KIND[part],
                        "velocity": 100,
                        "confidence": 1.0,
                        "source": "Songsterr",
                        "measure": mi,
                        "voice": vi,
                        "beatIndex": bi,
                    })
                cursor_whole += dur_whole
        measure_start += measure_len_whole * sec_per_whole

    notes.sort(key=lambda n: (n["time"], n["gmNote"]))
    return meta, drum, bpm, measure_starts, measure_start, notes


def write_midi(notes, out: Path, bpm: float):
    mid = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tempo = mido.bpm2tempo(bpm)
    tr.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    last_tick = 0
    for n in notes:
        tick = round(mido.second2tick(n["time"], 480, tempo))
        delta = max(0, tick - last_tick)
        tr.append(mido.Message("note_on", channel=9, note=int(n["gmNote"]), velocity=100, time=delta))
        tr.append(mido.Message("note_off", channel=9, note=int(n["gmNote"]), velocity=0, time=4))
        last_tick = tick + 4
    mid.save(out)


def write_dtx(notes, measure_starts, out: Path, bpm: float, offset: float, source: str):
    sec_per_whole = (60.0 / bpm) * 4.0
    rows = {}
    for n in notes:
        part = n["part"]
        ch = DTX_CHANNEL.get(part)
        if not ch:
            continue
        mi = int(n["measure"])
        musical_time = n["time"] - offset
        pos = (musical_time - measure_starts[mi]) / sec_per_whole
        slot = max(0, min(191, round(pos * 192)))
        rows.setdefault((mi, ch), {})[slot] = "01"

    lines = [
        "#TITLE:Luna Say Maybe - Drums",
        "#ARTIST:HATSUBOSHI GAKUEN",
        f"#BPM:{bpm:.6f}",
        f"#OFFSET:{offset:.3f}",
        f"#SOURCE:{source}",
    ]
    for (mi, ch), slots in sorted(rows.items()):
        cells = ["00"] * 192
        for slot, val in slots.items():
            cells[slot] = val
        lines.append(f"#{mi:03d}{ch}:{''.join(cells)}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("songsterr_json", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--offset", type=float, default=1.693)
    ap.add_argument("--audio-duration", type=float, default=266.945306)
    ap.add_argument("--source", default="Songsterr s1089457 rev 3745733 + original-audio alignment")
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    meta, drum, bpm, measure_starts, chart_duration, notes = extract_notes(args.songsterr_json, args.offset)

    payload = {
        "name": "Luna Say Maybe - Drums",
        "source": args.source,
        "songsterrSongId": meta.get("songId"),
        "songsterrRevisionId": meta.get("revisionId"),
        "bpm": bpm,
        "duration": args.audio_duration,
        "chartOffsetSec": args.offset,
        "alignment": {
            "method": "frequency-band transient correlation against original instrumental MP3",
            "globalOffsetSec": args.offset,
            "segmentBestOffsetsSec": [1.699,1.696,1.690,1.693,1.687],
            "driftRangeMs": 12,
        },
        "notes": notes,
    }
    (args.output / "Luna_say_maybe_FINAL_notes.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_midi(notes, args.output / "Luna_say_maybe_FINAL_drums.mid", bpm)
    write_dtx(
        notes, measure_starts, args.output / "Luna_say_maybe_FINAL.dtx",
        bpm, args.offset, args.source
    )

    counts = collections.Counter(n["part"] for n in notes)
    summary = {
        "source": args.source,
        "bpm": bpm,
        "measures": len(drum["measures"]),
        "chart_duration_sec_before_offset": round(chart_duration, 6),
        "audio_duration_sec": args.audio_duration,
        "notes": len(notes),
        "offset_sec": args.offset,
        "segment_offsets_sec": [1.699,1.696,1.690,1.693,1.687],
        "max_segment_drift_ms": 12,
        "part_counts": dict(sorted(counts.items())),
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
