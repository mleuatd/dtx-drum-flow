#!/usr/bin/env python3
"""Convert a Songsterr Guitar Pro 8 .gp source into DTX Drum Flow FINAL JSON.

The .gp file is a ZIP containing Content/score.gpif. No external Python
packages are required. This converter intentionally reads only the selected
percussion track and preserves the score grid (including dotted, triplet and
32nd-note timing).
"""
from __future__ import annotations

import argparse
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

GM_MAP = {
    35: ("BD", "kick", "kick"), 36: ("BD", "kick", "kick"),
    37: ("SN", "snare", "side-stick"), 38: ("SN", "snare", "snare"),
    39: ("SN", "snare", "clap"), 40: ("SN", "snare", "electric-snare"),
    41: ("FT", "toms", "low-floor-tom"), 43: ("FT", "toms", "high-floor-tom"),
    45: ("LT", "toms", "low-tom"), 47: ("LT", "toms", "low-mid-tom"),
    48: ("HT", "toms", "high-mid-tom"), 50: ("HT", "toms", "high-tom"),
    42: ("HH", "hihat", "closed"), 44: ("HH", "hihat", "pedal"),
    46: ("HH", "hihat", "open"),
    49: ("RC", "cymbals", "crash"), 52: ("RC", "cymbals", "china"),
    55: ("RC", "cymbals", "splash"), 57: ("RC", "cymbals", "crash-2"),
    51: ("RD", "cymbals", "ride"), 53: ("RD", "cymbals", "ride-bell"),
    59: ("RD", "cymbals", "ride-2"),
}
DYNAMIC_VELOCITY = {"PPP": 38, "PP": 48, "P": 60, "MP": 74, "MF": 88, "F": 100, "FF": 114, "FFF": 124}
QUARTER_LENGTH = {"Whole": 4.0, "Half": 2.0, "Quarter": 1.0, "Eighth": 0.5, "16th": 0.25, "32nd": 0.125, "64th": 0.0625}


def _index(parent):
    return {x.attrib["id"]: x for x in parent}


def _rhythm_info(beat, rhythms):
    rhythm = rhythms[beat.find("Rhythm").attrib["ref"]]
    name = rhythm.findtext("NoteValue")
    if name not in QUARTER_LENGTH:
        raise ValueError(f"Unsupported rhythm: {name}")
    q = QUARTER_LENGTH[name]
    dots = 0
    dot = rhythm.find("AugmentationDot")
    if dot is not None:
        dots = int(dot.attrib.get("count", "1"))
        q *= sum(0.5 ** i for i in range(dots + 1))
    tuplet = None
    tp = rhythm.find("PrimaryTuplet")
    if tp is not None:
        num, den = int(tp.attrib["num"]), int(tp.attrib["den"])
        q *= den / num
        tuplet = {"num": num, "den": den}
    return q, name, dots, tuplet


def _source_bpm(root):
    for a in root.findall("./MasterTrack/Automations/Automation"):
        if a.findtext("Type") == "Tempo":
            return float((a.findtext("Value") or "").split()[0])
    return 120.0


def convert(gp_path: Path, output_path: Path, *, track_index: int | None, bpm: float, duration: float, name: str = "叶えたい、ことばかり - Drums", artist: str = "月村手毬", song_id: int = 2808958, revision_id: int = 3694097) -> dict:
    with zipfile.ZipFile(gp_path) as zf:
        root = ET.fromstring(zf.read("Content/score.gpif"))

    master_bars = list(root.find("MasterBars"))
    bars, voices, beats, notes, rhythms = (_index(root.find(x)) for x in ("Bars", "Voices", "Beats", "Notes", "Rhythms"))
    source_bpm = _source_bpm(root)

    tracks = list(root.find("Tracks") or [])
    if track_index is None:
        named = []
        for i, track in enumerate(tracks):
            track_name = (track.findtext("Name") or "").strip().lower()
            if any(key in track_name for key in ("drum", "percussion", "battery", "batterie")):
                named.append(i)
        if len(named) == 1:
            track_index = named[0]
        elif named:
            track_index = named[0]
        else:
            raise ValueError("Could not auto-detect percussion track; pass --track-index")

    measure_starts = []
    clock = 0.0
    for m in master_bars:
        measure_starts.append(clock)
        num, den = map(int, m.findtext("Time").split("/"))
        clock += (num * 4 / den) * 60.0 / bpm

    result_notes = []
    for measure_index, master_bar in enumerate(master_bars):
        bar_ids = master_bar.findtext("Bars").split()
        if track_index >= len(bar_ids):
            raise ValueError(f"Track index {track_index} missing at measure {measure_index + 1}")
        bar = bars[bar_ids[track_index]]
        num, den = map(int, master_bar.findtext("Time").split("/"))
        expected_quarters = num * 4 / den

        for voice_slot, voice_id in enumerate((bar.findtext("Voices") or "").split()):
            if voice_id == "-1":
                continue
            beat_ids = (voices[voice_id].findtext("Beats") or "").split()
            position_q = 0.0
            for beat_index, beat_id in enumerate(beat_ids):
                beat = beats[beat_id]
                beat_q, rhythm_name, dots, tuplet = _rhythm_info(beat, rhythms)
                dynamic = (beat.findtext("Dynamic") or "MF").upper()
                velocity = DYNAMIC_VELOCITY.get(dynamic, 88)

                for note_id in (beat.findtext("Notes") or "").split():
                    note = notes[note_id]
                    gm_text = note.findtext("./Properties/Property[@name='Fret']/Fret")
                    if gm_text is None:
                        gm_text = note.findtext("./Properties/Property[@name='Midi']/Number")
                    gm = int(gm_text)
                    if gm not in GM_MAP:
                        raise ValueError(f"Unsupported GM drum note {gm} (note id {note_id})")
                    part, kind, articulation = GM_MAP[gm]
                    event_time = measure_starts[measure_index] + position_q * 60.0 / bpm
                    result_notes.append({
                        "time": round(event_time, 6),
                        "part": part,
                        "gmNote": gm,
                        "kind": kind,
                        "articulation": articulation,
                        "velocity": velocity,
                        "confidence": 0.98,
                        "source": f"Songsterr s{song_id} rev {revision_id} GP source",
                        "measure": measure_index + 1,
                        "voice": voice_slot,
                        "beatIndex": beat_index,
                        "rhythm": rhythm_name,
                        "dots": dots,
                        "tuplet": tuplet,
                        "alignmentOffsetSec": 0.0,
                    })
                position_q += beat_q

            if abs(position_q - expected_quarters) > 1e-6:
                raise ValueError(
                    f"Measure {measure_index + 1} voice {voice_slot}: "
                    f"{position_q} quarter-notes != expected {expected_quarters}"
                )

    result_notes.sort(key=lambda n: (n["time"], n["part"], n["gmNote"]))
    chart = {
        "name": name,
        "artist": artist,
        "source": f"Songsterr s{song_id} rev {revision_id} GP source + public BPM/duration cross-check",
        "songsterrSongId": song_id,
        "songsterrRevisionId": revision_id,
        "songsterrTrackIndex": track_index,
        "sourceScoreBpm": source_bpm,
        "bpm": bpm,
        "tempoDecision": f"Source score BPM {source_bpm:g}; chart BPM {bpm:g}. Original-audio millisecond alignment remains pending unless separately documented.",
        "measureCount": len(master_bars),
        "duration": duration,
        "chartOffsetSec": 0.0,
        "alignment": {
            "method": "score grid only; original-audio millisecond alignment pending user audio",
            "globalOffsetSec": 0.0,
            "pendingOriginalAudioSync": True,
        },
        "notes": result_notes,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(chart, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts = Counter(n["part"] for n in result_notes)
    print(f"wrote {output_path}: {len(result_notes)} notes, {len(master_bars)} measures, BPM {bpm} (source {source_bpm})")
    print("parts:", " ".join(f"{k}={counts[k]}" for k in sorted(counts)))
    return chart


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gp_source", type=Path)
    ap.add_argument("output_json", type=Path)
    ap.add_argument("--track-index", type=int, default=None)
    ap.add_argument("--bpm", type=float, default=143.0)
    ap.add_argument("--duration", type=float, default=246.0)
    ap.add_argument("--name", default="叶えたい、ことばかり - Drums")
    ap.add_argument("--artist", default="月村手毬")
    ap.add_argument("--song-id", type=int, default=2808958)
    ap.add_argument("--revision-id", type=int, default=3694097)
    args = ap.parse_args()
    convert(args.gp_source, args.output_json, track_index=args.track_index, bpm=args.bpm, duration=args.duration,
            name=args.name, artist=args.artist, song_id=args.song_id, revision_id=args.revision_id)


if __name__ == "__main__":
    main()
