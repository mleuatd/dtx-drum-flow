from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

import pipeline


def synth_click_track(path: Path, times: list[float], sr: int = 44100, duration: float = 3.0) -> None:
    y = np.zeros(int(sr * duration), dtype=np.float32)
    for t in times:
        i = int(round(t * sr))
        # short broadband transient with a decaying tail
        n = min(int(sr * 0.025), len(y) - i)
        if n <= 0:
            continue
        rng = np.random.default_rng(int(t * 100000) + 123)
        env = np.exp(-np.linspace(0, 8, n, dtype=np.float32))
        y[i:i+n] += (rng.standard_normal(n).astype(np.float32) * env * 0.8)
    sf.write(path, y, sr)


def nearest_errors(found: list[float], expected: list[float]) -> list[float]:
    errs = []
    for t in expected:
        errs.append(min(abs(x - t) for x in found))
    return errs


def test_detect_onsets_timing():
    expected = [0.50, 1.00, 1.50, 2.00, 2.50]
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "clicks.wav"
        synth_click_track(wav, expected)
        got = pipeline.detect_onsets(wav, "unknown", "synthetic")
        times = [x.time for x in got]
        assert len(times) >= len(expected) - 1, (times, expected)
        errs = nearest_errors(times, expected)
        assert max(errs) <= 0.035, errs
        assert sum(errs)/len(errs) <= 0.020, errs


def test_global_offset_estimation():
    reference = [pipeline.Candidate(t, "unknown", 1.0, "ref") for t in [0.5, 1.0, 1.5, 2.0, 2.5]]
    # target is 180 ms late; correct offset should be roughly -0.180 sec
    target = [pipeline.Candidate(t + 0.180, "snare", 1.0, "target") for t in [0.5, 1.0, 1.5, 2.0, 2.5]]
    off = pipeline.estimate_global_offset(reference, target)
    assert abs(off + 0.180) <= 0.012, off


def test_consensus_prefers_multi_source_and_snaps_to_mix():
    mix = [pipeline.Candidate(1.000, "unknown", 1.0, "original-mix")]
    cands = [
        pipeline.Candidate(0.992, "snare", 0.9, "drumsep-snare"),
        pipeline.Candidate(1.010, "snare", 0.8, "adtof-plus"),
        pipeline.Candidate(0.999, "snare", 0.7, "demucs-drums"),
    ]
    beats = np.array([1.0])
    notes = pipeline.consolidate(cands, beats, mix)
    assert len(notes) == 1
    n = notes[0]
    assert n.kind == "snare"
    assert abs(n.time - 1.000) <= 0.001
    assert n.votes == 3
    assert n.confidence >= 0.75


def test_json_shape_is_browser_compatible():
    n = pipeline.FinalNote(1.234, "kick", 100, 0.91, 2, ["a", "b"])
    payload = {"bpm": 120.0, "notes": [pipeline.asdict(n)]}
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded["notes"][0]["kind"] == "kick"
    assert 0 <= decoded["notes"][0]["confidence"] <= 1


if __name__ == "__main__":
    test_detect_onsets_timing()
    test_global_offset_estimation()
    test_consensus_prefers_multi_source_and_snaps_to_mix()
    test_json_shape_is_browser_compatible()
    print("synthetic audio tests: PASS")
