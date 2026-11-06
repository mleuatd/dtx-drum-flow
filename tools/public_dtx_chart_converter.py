#!/usr/bin/env python3
"""Convert a locally available DTX score into drum-event metadata.
Source score and any sound/video assets are NOT copied to the output.
The caller is responsible for ensuring their distribution/use rights.
"""
import argparse
import json
import math
import re
from pathlib import Path

CHANNELS = {
    "11": ("HH", 42, "hihat-close"),
    "12": ("SN", 38, "snare"),
    "13": ("BD", 36, "kick"),
    "14": ("HT", 50, "high-tom"),
    "15": ("LT", 47, "low-tom"),
    "16": ("RC", 49, "right-crash"),
    "17": ("FT", 41, "floor-tom"),
    "18": ("HH", 46, "hihat-open"),
    "19": ("RD", 51, "ride"),
    "1A": ("LC", 49, "left-crash"),
    "1B": ("LB", 35, "left-bass"),
    "1C": ("LP", 44, "hihat-foot"),
    "61": ("SN", 38, "snare-ghost"),
}
KIND = {
    "BD":"kick","LB":"kick","SN":"snare",
    "HH":"hihat","LP":"hihat",
    "HT":"toms","LT":"toms","FT":"toms",
    "LC":"cymbals","RC":"cymbals","RD":"cymbals",
}

def decode_dtx(raw):
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw[:100].count(0) > 20:
        return raw.decode("utf-16-le")
    for encoding in ("utf-8-sig", "cp932"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")

def parse_dtx(raw, difficulty, source_url):
    lines = decode_dtx(raw).splitlines()
    headers = {}
    bpm_ids = {}
    channels = []
    bar_scales = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line.startswith("#"):
            continue
        line = line.split(";", 1)[0].strip()
        m = re.match(r"^#(\d{3})([A-Za-z0-9]{2})\s*:\s*(.+)$", line)
        if m:
            measure, channel, value = int(m[1]), m[2].upper(), m[3].strip()
            if channel == "02":
                try:
                    scale = float(value)
                    if math.isfinite(scale) and 0.1 <= scale <= 16:
                        bar_scales[measure] = scale
                except ValueError:
                    pass
            elif channel in CHANNELS or channel in ("03", "08"):
                data = re.sub(r"\s+", "", value).upper()
                if len(data) % 2 or re.search(r"[^0-9A-Z]", data):
                    continue
                for j in range(0, len(data), 2):
                    code = data[j:j+2]
                    if code != "00":
                        channels.append((measure, channel, j/len(data), code))
            continue
        mh = re.match(r"^#([A-Za-z][A-Za-z0-9]*)(?::|\s+)\s*(.*)$", line)
        if mh:
            key, val = mh[1].upper(), mh[2].strip()
            if key.startswith("BPM") and len(key) == 5:
                try:
                    bpm_ids[key[-2:]] = float(val)
                except ValueError:
                    pass
            else:
                headers[key] = val
    try:
        bpm = float(headers.get("BPM") or 120)
    except ValueError:
        bpm = 120
    if not math.isfinite(bpm) or bpm <= 0:
        bpm = 120.0
    events_by_measure = {}
    for measure, channel, frac, code in channels:
        events_by_measure.setdefault(measure, []).append((frac, channel, code))
    max_measure = max([0, *events_by_measure, *bar_scales])
    time = 0.0
    notes, tempo_changes = [], []
    last_note_time = 0.0
    for measure in range(max_measure+1):
        quarter_beats = 4.0 * bar_scales.get(measure, 1.0)
        events = sorted(events_by_measure.get(measure, []), key=lambda e: (e[0], 0 if e[1] in ("03","08") else 1))
        last_frac = 0.0
        for frac, channel, code in events:
            time += (frac-last_frac) * quarter_beats * 60 / bpm
            last_frac = frac
            if channel in ("03","08"):
                try:
                    next_bpm = float(int(code,16)) if channel=="03" else bpm_ids.get(code)
                    if next_bpm and math.isfinite(next_bpm) and next_bpm > 0:
                        bpm = next_bpm
                        tempo_changes.append({"time":round(time,6),"bpm":bpm,"measure":measure+1})
                except ValueError:
                    pass
                continue
            part, gm, articulation = CHANNELS[channel]
            notes.append({
                "time":round(max(0,time),6),
                "part":part,"gmNote":gm,"kind":KIND[part],
                "articulation":articulation,"velocity":102,
                "measure":measure+1,
            })
            last_note_time = max(last_note_time, time)
        time += (1.0-last_frac) * quarter_beats * 60 / bpm
    notes.sort(key=lambda x:(x["time"],x["part"]))
    title = headers.get("TITLE","Campus mode!!")
    if "Campus" not in title: raise ValueError("DTX title mismatch")
    return {
        "name":f"Campus mode!! - Drums ({difficulty.upper()})",
        "artist":"初星学園",
        "source":f"Furukon public DTX simfile: {source_url}",
        "sourceFormat":"DTX (UTF-16)",
        "sourceSongId":462,
        "difficulty":difficulty,
        "dLevel":int(headers.get("DLEVEL","0"))/10,
        "bpm":float(headers.get("BPM","183")),
        "duration":round(max(last_note_time+2.0,time),6),
        "measureCount":max_measure+1,
        "tempoChanges":tempo_changes,
        "alignment":{"method":"Original DTX beat grid with variable BPM and measure lengths","pendingOriginalAudioSync":True},
        "notes":notes,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("destination")
    p.add_argument("--difficulty",required=True,choices=["bas","adv","ext"])
    p.add_argument("--source-url",default="https://dtx.furukon.com/?p=1&search=Campus%20mode")
    args=p.parse_args()
    chart=parse_dtx(Path(args.source).read_bytes(),args.difficulty,args.source_url)
    if len(chart["notes"]) < 50:
        raise RuntimeError("Not enough drum notes were extracted")
    output=Path(args.destination)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(chart,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print(json.dumps({k:chart[k] for k in ("name","difficulty","bpm","duration","measureCount")},ensure_ascii=False))
    print("NOTE_COUNT",len(chart["notes"]))
    print("TEMPO_EVENTS",len(chart["tempoChanges"]))
    from collections import Counter
    print("PART_COUNTS",dict(Counter(n["part"] for n in chart["notes"])))
if __name__=="__main__":main()
