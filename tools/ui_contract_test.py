from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
html=(root/"site/index.html").read_text(encoding="utf-8")
js=(root/"site/app.js").read_text(encoding="utf-8")
parsers=(root/"site/parsers.js").read_text(encoding="utf-8")
css=(root/"site/styles.css").read_text(encoding="utf-8")

checks = {
    "11 drum lanes": 'const PARTS=["LC","HH","SN","HT","LT","FT","RC","RD","LP","LB","BD"]' in js,
    "Luna final chart button": 'id="loadLuna"' in html and 'Luna say maybe' in html,
    "Kanaetai final chart button": 'id="loadKanaetai"' in html and '叶えたい、ことばかり' in html and 'Kanaetai_koto_bakari_FINAL_notes.json' in js,
    "original sound toggle": 'id="originalSound"' in html and '$("originalSound").onchange' in js,
    "drum sound toggle": 'id="drumSound"' in html and '$("drumSound").onchange' in js,
    "sound toggles horizontal": '.sound-controls' in css and 'grid-template-columns:1fr 1fr' in css,
    "note speed range": re.search(r'id="noteSpeed"[^>]*min="0\.5"[^>]*max="8"[^>]*value="1"[^>]*step="0\.1"', html) is not None,
    "note speed separate variable": re.search(r'\bnoteSpeed\s*=\s*1\b', js) is not None and 'const lookAhead=3.3/noteSpeed' in js,
    "music speed control remains": 'id="speed"' in html and '音楽速度' in html,
    "notes never pass judgment line": 'if(dt<0||dt>lookAhead)continue' in js,
    "judgment line flashes": 'const hitNow=' in js and 'ctx.shadowBlur=hitNow?22:0' in js,
    "five second seek": '$("rewind5").onclick=()=>seek(chartTimeFromClock()-5)' in js and '$("forward5").onclick=()=>seek(chartTimeFromClock()+5)' in js,
    "four measure buttons": '$("rewindMeasure").onclick=()=>seek(chartTimeFromClock()-measureSeconds()*4)' in js and '$("forwardMeasure").onclick=()=>seek(chartTimeFromClock()+measureSeconds()*4)' in js,
    "four measure double tap": 'if(now-last<350)seek(chartTimeFromClock()+dir*measureSeconds()*4)' in js,
    "timeline seek": '$("timeline").oninput=e=>seek(Number(e.target.value))' in js,
    "audio sync alignment": 'realignNotes(chart.notes,onsets,chart.bpm)' in js,
    "chart JSON export": 'id="exportJson"' in html and 'chartToJson()' in js,
    "drag and drop": 'id="dropZone"' in html and 'dropZone.addEventListener("drop"' in js,
    "MIDI import": 'ext==="mid"||ext==="midi"' in parsers,
    "DTX/GDA import": 'ext==="dtx"||ext==="gda"' in parsers,
    "JSON import": 'if(ext==="json")' in parsers,
    "DTX OFFSET": '#OFFSET' in parsers,
    "Xperia viewport": 'viewport-fit=cover' in html and 'user-scalable=no' in html,
    "fixed mobile transport": '.mobile-transport' in css and 'position:fixed' in css,
}

failed=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items():
    print(("PASS" if ok else "FAIL"), name)
if failed:
    raise SystemExit("UI contract failures: "+", ".join(failed))
print(f"PASS all {len(checks)} UI contract checks")
