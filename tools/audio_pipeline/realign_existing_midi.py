from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import librosa
import mido
import numpy as np

GM_FAMILY = {
    35: "kick", 36: "kick",
    37: "snare", 38: "snare", 39: "snare", 40: "snare",
    41: "toms", 43: "toms", 45: "toms", 47: "toms", 48: "toms", 50: "toms",
    42: "hihat", 44: "hihat", 46: "hihat",
    49: "cymbals", 51: "cymbals", 52: "cymbals", 53: "cymbals",
    55: "cymbals", 57: "cymbals", 59: "cymbals",
}
GM_PART = {
    35: "BD", 36: "BD",
    37: "SN", 38: "SN", 39: "SN", 40: "SN",
    41: "FT", 43: "FT", 45: "LT", 47: "LT", 48: "HT", 50: "HT",
    42: "HH", 44: "HH", 46: "HH",
    49: "RC", 51: "RD", 52: "RC", 53: "RD", 55: "RC", 57: "RC", 59: "RD",
}
BAND = {
    "kick": (30, 180),
    "toms": (100, 700),
    "snare": (500, 6000),
    "hihat": (5000, 11000),
    "cymbals": (3500, 11000),
}
THRESHOLD = {"kick": 1.4, "snare": 2.3, "toms": 2.1, "hihat": 1.8, "cymbals": 1.8}


def read_midi(path: Path):
    mid = mido.MidiFile(path)
    tempo = 500000
    t = 0.0
    out = []
    for msg in mido.merge_tracks(mid.tracks):
        t += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
        if msg.type == "set_tempo":
            tempo = msg.tempo
        elif msg.type == "note_on" and msg.velocity > 0 and msg.note in GM_FAMILY:
            out.append((t, msg.note, msg.velocity))
    return out


def make_band_flux(audio: Path, sr: int = 22050, hop: int = 128):
    y, _ = librosa.load(audio, sr=sr, mono=True)
    if not len(y):
        raise ValueError("audio is empty")
    y = y / (np.max(np.abs(y)) + 1e-9)
    spec = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop, win_length=2048)) ** 2
    freq = librosa.fft_frequencies(sr=sr, n_fft=2048)
    times = librosa.frames_to_time(np.arange(spec.shape[1]), sr=sr, hop_length=hop)
    bands = {}
    for family, (lo, hi) in BAND.items():
        idx = (freq >= lo) & (freq < hi)
        x = np.log1p(10 * spec[idx])
        d = np.maximum(0, np.diff(x, axis=1, prepend=x[:, :1]))
        flux = d.mean(axis=0)
        med = np.median(flux)
        mad = np.median(np.abs(flux - med)) + 1e-9
        bands[family] = (flux - med) / (1.4826 * mad)
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
    tempo = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=256)[0]
    tempo = float(np.ravel(tempo)[0])
    return y, sr, times, bands, tempo


def interp(times: np.ndarray, env: np.ndarray, ts: np.ndarray):
    idx = np.clip(np.searchsorted(times, ts), 1, len(times) - 1)
    x0, x1 = times[idx - 1], times[idx]
    w = (ts - x0) / (x1 - x0 + 1e-12)
    return env[idx - 1] * (1 - w) + env[idx] * w


def estimate_family_offsets(notes, times, bands, max_offset=0.25):
    groups = defaultdict(list)
    for t, note, _ in notes:
        groups[GM_FAMILY[note]].append(t)
    grid = np.arange(-max_offset, max_offset + 1e-9, 0.002)
    offsets = {}
    for family, vals in groups.items():
        arr = np.asarray(vals, dtype=float)
        scores = [np.mean(interp(times, bands[family], arr + off)) for off in grid]
        offsets[family] = float(grid[int(np.argmax(scores))])
    return offsets


def realign(notes, times, bands, offsets):
    corrected = []
    for original_time, gm_note, velocity in notes:
        family = GM_FAMILY[gm_note]
        base = original_time + offsets[family]
        env = bands[family]
        indexes = np.where((times >= base - 0.09) & (times <= base + 0.09))[0]
        if len(indexes):
            j = indexes[np.argmax(env[indexes])]
            peak_time = float(times[j])
            peak_z = float(env[j])
            local_delta = peak_time - base
            snapped = peak_z >= THRESHOLD[family] and abs(local_delta) <= 0.06
            new_time = peak_time if snapped else base
            confidence = (1 / (1 + math.exp(-(peak_z - THRESHOLD[family])))) * max(
                0.0, 1 - abs(local_delta) / 0.09
            )
            if not snapped:
                confidence *= 0.6
        else:
            new_time, peak_z, local_delta, snapped, confidence = base, 0.0, 0.0, False, 0.1
        corrected.append(
            {
                "time": round(new_time, 6),
                "originalTime": round(original_time, 6),
                "gmNote": gm_note,
                "part": GM_PART[gm_note],
                "kind": family,
                "velocity": velocity,
                "confidence": round(float(np.clip(confidence, 0, 1)), 4),
                "globalOffsetMs": round(offsets[family] * 1000, 2),
                "localShiftMs": round((new_time - base) * 1000, 2),
                "peakZ": round(peak_z, 3),
                "snapped": snapped,
            }
        )
    return corrected


def summarize(corrected):
    result = {}
    for family in BAND:
        arr = [n for n in corrected if n["kind"] == family]
        if not arr:
            continue
        result[family] = {
            "count": len(arr),
            "globalOffsetMs": arr[0]["globalOffsetMs"],
            "snappedPct": round(100 * np.mean([n["snapped"] for n in arr]), 1),
            "meanAbsTotalShiftMs": round(
                np.mean([abs(n["time"] - n["originalTime"]) for n in arr]) * 1000, 2
            ),
            "p90AbsTotalShiftMs": round(
                np.percentile([abs(n["time"] - n["originalTime"]) for n in arr], 90) * 1000, 2
            ),
            "meanConfidence": round(float(np.mean([n["confidence"] for n in arr])), 3),
            "lowConfidencePct": round(100 * np.mean([n["confidence"] < 0.35 for n in arr]), 1),
        }
    return result


def write_midi(corrected, path: Path, bpm: float):
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    last_tick = 0
    for item in sorted(corrected, key=lambda x: x["time"]):
        tick = round(mido.second2tick(item["time"], 480, tempo))
        delta = max(0, tick - last_tick)
        track.append(
            mido.Message(
                "note_on",
                channel=9,
                note=int(item["gmNote"]),
                velocity=int(item["velocity"]),
                time=delta,
            )
        )
        track.append(
            mido.Message("note_off", channel=9, note=int(item["gmNote"]), velocity=0, time=6)
        )
        last_tick = tick + 6
    mid.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", type=Path)
    ap.add_argument("midi", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--bpm", type=float)
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    notes = read_midi(args.midi)
    y, sr, times, bands, estimated_bpm = make_band_flux(args.audio)
    offsets = estimate_family_offsets(notes, times, bands)
    corrected = realign(notes, times, bands, offsets)
    bpm = args.bpm or estimated_bpm

    notes_payload = {
        "name": args.audio.stem,
        "bpm": bpm,
        "duration": len(y) / sr,
        "notes": corrected,
    }
    diagnostics = {
        "audioDurationSec": round(len(y) / sr, 3),
        "estimatedBpm": round(estimated_bpm, 3),
        "inputMidiNotes": len(notes),
        "familySummary": summarize(corrected),
        "method": "frequency-band spectral-flux evidence + per-family global offset + local transient snap",
    }

    (args.output / "notes_corrected.json").write_text(
        json.dumps(notes_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.output / "diagnostics.json").write_text(
        json.dumps(diagnostics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_midi(corrected, args.output / "drums_corrected.mid", bpm)
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
