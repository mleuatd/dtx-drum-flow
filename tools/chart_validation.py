from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_PARTS = {"LC", "HH", "SN", "HT", "LT", "FT", "RC", "RD", "LP", "LB", "BD"}
REQUIRED_FIELDS = {"time", "part", "gmNote", "kind", "velocity", "confidence", "source", "measure", "voice", "beatIndex"}
GM_PART = {
    35:"BD",36:"BD",37:"SN",38:"SN",39:"SN",40:"SN",41:"FT",43:"FT",
    45:"LT",47:"LT",48:"HT",50:"HT",42:"HH",44:"HH",46:"HH",
    49:"RC",52:"RC",55:"RC",57:"RC",51:"RD",53:"RD",59:"RD",
}

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def validate_common(chart, label):
    notes = chart["notes"]
    assert notes, f"{label}: no notes"
    times = [float(n["time"]) for n in notes]
    assert times == sorted(times), f"{label}: notes are not sorted"
    assert min(times) >= 0, f"{label}: negative note time"
    assert max(times) <= float(chart["duration"]) + 0.001, f"{label}: note exceeds duration"
    for i, n in enumerate(notes):
        missing = REQUIRED_FIELDS - set(n)
        assert not missing, f"{label}: note {i} missing {sorted(missing)}"
        assert n["part"] in ALLOWED_PARTS, f"{label}: invalid part {n['part']}"
        gm = int(n["gmNote"])
        if gm in GM_PART:
            assert n["part"] == GM_PART[gm], f"{label}: GM {gm} mapped to {n['part']}"
        assert int(n["measure"]) >= 1, f"{label}: invalid measure"
        assert 0 <= int(n["velocity"]) <= 127, f"{label}: invalid velocity"

    # Simultaneous kit hits are valid; pathological import duplication is not.
    simultaneous = Counter(times)
    assert max(simultaneous.values()) <= 8, f"{label}: excessive simultaneous notes"

    # Detect accidental machine-gun clusters inside 100 ms.
    q = deque()
    max_window = 0
    for t in times:
        q.append(t)
        while q and t - q[0] > 0.1:
            q.popleft()
        max_window = max(max_window, len(q))
    assert max_window <= 18, f"{label}: excessive 100ms density {max_window}"

    return Counter(n["part"] for n in notes)

luna = load("site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json")
luna_parts = validate_common(luna, "Luna")
assert len(luna["notes"]) == 2158, f"Luna regression: {len(luna['notes'])} notes"
assert float(luna["bpm"]) == 139.0, "Luna regression: BPM changed"
# The preserved Luna FINAL has played notes through measure 148; the source arrangement
# is roughly 150 measures including trailing/rest-only score space. Test the actual FINAL
# representation so this regression guard never requires mutating the existing chart.
assert max(int(n["measure"]) for n in luna["notes"]) == 148, "Luna regression: final played measure changed"

kana = load("site/charts/kanaetai_koto_bakari/Kanaetai_koto_bakari_FINAL_notes.json")
kana_parts = validate_common(kana, "Kanaetai")
assert len(kana["notes"]) == 1945, f"Kanaetai: expected 1945 notes, got {len(kana['notes'])}"
assert float(kana["bpm"]) == 143.0, "Kanaetai: normalized BPM must be 143"
assert float(kana["sourceScoreBpm"]) == 144.0, "Kanaetai: source score BPM must remain documented"
assert int(kana["measureCount"]) == 144, "Kanaetai: measure count mismatch"
assert max(int(n["measure"]) for n in kana["notes"]) == 144, "Kanaetai: final measure missing"
assert 245.0 <= float(kana["duration"]) <= 247.5, "Kanaetai: duration inconsistent with released ~4:06 track"
assert set(("BD","SN","HH","HT","LT","FT","RC","RD")) <= set(kana_parts), "Kanaetai: required drum parts missing"

# The active chart has no unexplained long silence between played events.
event_times = sorted(set(float(n["time"]) for n in kana["notes"]))
max_gap = max(b-a for a,b in zip(event_times,event_times[1:]))
assert max_gap < 4.0, f"Kanaetai: suspicious internal gap {max_gap:.3f}s"

# Verify preservation of source rhythmic detail.
assert any(n.get("tuplet") == {"num":3,"den":2} for n in kana["notes"]), "Kanaetai: triplets missing"
assert any(n.get("rhythm") == "32nd" for n in kana["notes"]), "Kanaetai: 32nd notes missing"
assert all(float(n.get("alignmentOffsetSec", 0)) == 0 for n in kana["notes"]), "Kanaetai: pre-audio alignment must be zero"
assert kana.get("alignment", {}).get("pendingOriginalAudioSync") is True, "Kanaetai: sync-pending flag missing"

print("PASS Luna regression:", len(luna["notes"]), "notes", dict(sorted(luna_parts.items())))
print("PASS Kanaetai:", len(kana["notes"]), "notes", dict(sorted(kana_parts.items())), "max_gap", round(max_gap,3))
