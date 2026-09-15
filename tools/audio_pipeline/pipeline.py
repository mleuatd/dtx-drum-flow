from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import librosa
import mido
import numpy as np
import soundfile as sf

GM = {"kick":36, "snare":38, "hihat":42, "toms":45, "cymbals":49, "unknown":37}
PART = {36:"BD",35:"BD",38:"SN",40:"SN",42:"HH",44:"HH",46:"HH",41:"FT",43:"FT",45:"LT",47:"LT",48:"HT",50:"HT",49:"RC",51:"RD",52:"RC",55:"RC",57:"RC",53:"RD",59:"RD"}

@dataclass
class Candidate:
    time: float
    kind: str
    strength: float
    source: str

@dataclass
class FinalNote:
    time: float
    kind: str
    velocity: int
    confidence: float
    votes: int
    sources: list[str]


def cmd_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def detect_onsets(path: Path, kind: str, source: str) -> list[Candidate]:
    y, sr = librosa.load(path, sr=44100, mono=True)
    if len(y) == 0:
        return []
    env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
    frames = librosa.onset.onset_detect(onset_envelope=env, sr=sr, units="frames", backtrack=True, pre_max=3, post_max=3, pre_avg=8, post_avg=8, delta=0.12, wait=2)
    times = librosa.frames_to_time(frames, sr=sr)
    mx = float(np.max(env)) if len(env) else 1.0
    out = []
    for f, t in zip(frames, times):
        s = float(env[f] / mx) if mx > 0 else 0.5
        out.append(Candidate(float(t), kind, s, source))
    return out


def demucs_separate(audio: Path, work: Path) -> dict[str, Path]:
    if not cmd_exists("demucs"):
        return {}
    out = work / "demucs"
    out.mkdir(parents=True, exist_ok=True)
    run(["demucs", "-n", "htdemucs", "-o", str(out), str(audio)])
    root = out / "htdemucs" / audio.stem
    result = {}
    for k in ("drums","bass","other","vocals"):
        p = root / f"{k}.wav"
        if p.exists():
            result[k] = p
    return result


def drumsep_separate(drums: Path, bass: Path | None, work: Path) -> dict[str, Path]:
    if not cmd_exists("drumsep"):
        return {}
    out = work / "drumsep"
    out.mkdir(parents=True, exist_ok=True)
    cmd = ["drumsep", str(drums), "-o", str(out)]
    if bass and bass.exists():
        cmd += ["--bass", str(bass)]
    run(cmd)
    aliases = {
        "kick":["kick.wav"], "snare":["snare.wav"], "hihat":["hihat.wav","hi-hat.wav"],
        "cymbals":["cymbals.wav","cymbal.wav"], "toms":["toms.wav","tom.wav"]
    }
    found = {}
    for k, names in aliases.items():
        for n in names:
            p = out / n
            if p.exists():
                found[k] = p
                break
    return found


def run_adtof(audio: Path, work: Path) -> Path | None:
    """Run ADTOF Plus when its CLI is available. No model/code is vendored here."""
    if not cmd_exists("adtof-transcribe"):
        return None
    out = work / "adtof.mid"
    try:
        run(["adtof-transcribe", "--audio_path", str(audio), "--output_path", str(out)])
    except subprocess.CalledProcessError:
        return None
    return out if out.exists() else None


def midi_candidates(path: Path, source: str) -> list[Candidate]:
    mid = mido.MidiFile(path)
    tempo = 500000
    absolute = 0.0
    out = []
    for msg in mido.merge_tracks(mid.tracks):
        absolute += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
        if msg.type == "set_tempo":
            tempo = msg.tempo
        elif msg.type == "note_on" and msg.velocity > 0:
            kind = {
                "BD":"kick","SN":"snare","HH":"hihat","HT":"toms","LT":"toms","FT":"toms",
                "RC":"cymbals","RD":"cymbals","LC":"cymbals"
            }.get(PART.get(msg.note, ""), "unknown")
            out.append(Candidate(absolute, kind, msg.velocity / 127.0, source))
    return out


def estimate_bpm(audio: Path) -> tuple[float, np.ndarray]:
    y, sr = librosa.load(audio, sr=22050, mono=True)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, units="time")
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo.ravel()[0])
    return float(tempo), np.asarray(beats, dtype=float)


def nearest_beat_score(t: float, beats: np.ndarray) -> float:
    if len(beats) == 0:
        return 0.5
    d = float(np.min(np.abs(beats - t)))
    return max(0.0, 1.0 - d / 0.08)


def cluster(cands: list[Candidate], window: float = 0.045) -> list[list[Candidate]]:
    cands = sorted(cands, key=lambda c: c.time)
    groups: list[list[Candidate]] = []
    for c in cands:
        if not groups or c.time - np.mean([x.time for x in groups[-1]]) > window:
            groups.append([c])
        else:
            groups[-1].append(c)
    return groups


def choose_kind(group: list[Candidate]) -> str:
    scores: dict[str, float] = {}
    for c in group:
        scores[c.kind] = scores.get(c.kind, 0.0) + 0.5 + c.strength
    return max(scores, key=scores.get)


def consolidate(cands: list[Candidate], beats: np.ndarray, mix_onsets: list[Candidate]) -> list[FinalNote]:
    mix_times = np.array([c.time for c in mix_onsets], dtype=float)
    finals = []
    for g in cluster(cands):
        sources = sorted(set(c.source for c in g))
        kind = choose_kind(g)
        weights = np.array([0.35 + c.strength for c in g], dtype=float)
        times = np.array([c.time for c in g], dtype=float)
        t = float(np.average(times, weights=weights))

        # snap to original-mix transient only when close enough
        snap_bonus = 0.0
        if len(mix_times):
            i = int(np.argmin(np.abs(mix_times - t)))
            d = abs(float(mix_times[i] - t))
            if d <= 0.035:
                t = float(mix_times[i])
                snap_bonus = 0.15 * (1 - d / 0.035)

        votes = len(sources)
        beat = nearest_beat_score(t, beats)
        strength = float(np.mean([c.strength for c in g]))
        confidence = min(1.0, 0.18 + votes * 0.18 + strength * 0.22 + beat * 0.18 + snap_bonus)

        # very weak single-source hits are omitted
        if votes == 1 and confidence < 0.47:
            continue
        velocity = int(np.clip(round(38 + 89 * min(1.0, strength)), 1, 127))
        finals.append(FinalNote(t, kind, velocity, confidence, votes, sources))
    return sorted(finals, key=lambda n: n.time)


def write_midi(notes: Iterable[FinalNote], out: Path, bpm: float) -> None:
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    tempo = mido.bpm2tempo(max(30, min(300, bpm)))
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    last_tick = 0
    for n in notes:
        tick = round(mido.second2tick(n.time, mid.ticks_per_beat, tempo))
        dt = max(0, tick - last_tick)
        track.append(mido.Message("note_on", channel=9, note=GM.get(n.kind,37), velocity=n.velocity, time=dt))
        track.append(mido.Message("note_off", channel=9, note=GM.get(n.kind,37), velocity=0, time=12))
        last_tick = tick + 12
    mid.save(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", type=Path)
    ap.add_argument("-o","--output", type=Path, required=True)
    ap.add_argument("--midi", type=Path, nargs="*", default=[])
    ap.add_argument("--bpm", type=float)
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    work = args.output / "stems"
    work.mkdir(exist_ok=True)

    bpm, beats = estimate_bpm(args.audio)
    if args.bpm:
        bpm = args.bpm

    all_candidates: list[Candidate] = []
    mix_onsets = detect_onsets(args.audio, "unknown", "original-mix")
    all_candidates.extend(mix_onsets)

    demucs = demucs_separate(args.audio, work)
    if "drums" in demucs:
        all_candidates += detect_onsets(demucs["drums"], "unknown", "demucs-drums")
        sub = drumsep_separate(demucs["drums"], demucs.get("bass"), work)
        for kind, p in sub.items():
            all_candidates += detect_onsets(p, kind, f"drumsep-{kind}")

    adtof_midi = run_adtof(args.audio, work)
    if adtof_midi:
        all_candidates += midi_candidates(adtof_midi, "adtof-plus")

    for i, p in enumerate(args.midi):
        all_candidates += midi_candidates(p, f"midi-{i+1}")

    finals = consolidate(all_candidates, beats, mix_onsets)

    with open(args.output/"notes.json","w",encoding="utf-8") as f:
        json.dump({"bpm":bpm,"notes":[asdict(n) for n in finals]},f,ensure_ascii=False,indent=2)
    with open(args.output/"diagnostics.json","w",encoding="utf-8") as f:
        json.dump({
            "bpm":bpm,
            "candidate_count":len(all_candidates),
            "final_count":len(finals),
            "demucs_used":bool(demucs),
            "adtof_used":bool(adtof_midi),
            "sources":sorted(set(c.source for c in all_candidates)),
        },f,ensure_ascii=False,indent=2)
    write_midi(finals,args.output/"drums.mid",bpm)
    print(f"done: {len(finals)} notes, bpm={bpm:.2f}")


if __name__ == "__main__":
    main()
