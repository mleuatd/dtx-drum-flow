from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
html=(root/"site/index.html").read_text(encoding="utf-8")
js=(root/"site/app.js").read_text(encoding="utf-8")
parsers=(root/"site/parsers.js").read_text(encoding="utf-8")
css=(root/"site/styles.css").read_text(encoding="utf-8")
character_js=(root/"site/character-prototype.js").read_text(encoding="utf-8")

checks = {
    "11 drum lanes": 'const PARTS=["LB","LC","HH","LP","SN","BD","HT","LT","FT","RD","RC"]' in js and 'SN","BD","HT' in js,
    "song selection combobox": 'id="songSelect"' in html and '<option value="luna">Luna say maybe</option>' in html and '<option value="kanaetai">叶えたい、ことばかり</option>' in html and '<option value="ittai">一体いつから</option>' in html,
    "song selection loader": '$("songSelect").addEventListener("change",loadSelectedSong)' in js and 'Luna_say_maybe_FINAL_notes.json' in js and 'Kanaetai_koto_bakari_FINAL_notes.json' in js and 'Ittai_itsukara_FINAL_notes.json' in js,
    "original sound toggle": 'id="originalSound"' in html and '$("originalSound").onchange' in js,
    "drum sound toggle": 'id="drumSound"' in html and '$("drumSound").onchange' in js,
    "metronome toggle": 'id="metronomeSound"' in html and 'id="metronomeSoundState"' in html and '$("metronomeSound").onchange' in js,
    "metronome scheduler": 'function scheduleMetronome(horizon)' in js and 'nextMetronomeBeat' in js and 'metronomeAt(nextMetronomeBeat,target)' in js,
    "sound toggles horizontal": '.sound-controls' in css and 'grid-template-columns:1fr 1fr' in css,
    "note speed range": re.search(r'id="noteSpeed"[^>]*min="0\.5"[^>]*max="8"[^>]*value="1"[^>]*step="0\.1"', html) is not None,
    "note speed separate variable": 'noteSpeed=1' in js and 'lookAhead=3.3/noteSpeed' in js,
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
    "playback independent from audio clock": 'playAnchorPerf=performance.now()' in js and '(performance.now()-playAnchorPerf)/1000' in js,
    "play button immediate state": '$("playPause").textContent="一時停止 ❚❚"' in js and 'setStatus("再生中")' in js,
    "character module cache bust": 'character-prototype.js?v=20260916-16m-final' in js and 'app.js?v=20260916-16m-final' in html and 'styles.css?v=20260916-16m-final' in html,
    "character canvas stays transparent": 'isLuna?"rgba(7,9,22,.20)":"#0e172a"' in js and '.stage canvas{' in css and 'background:transparent' in css,
    "character layer visible behind notes": '.character-backdrop.active{opacity:.9}' in css and '.stage canvas{' in css and 'z-index:1' in css,
    "sixteen measure runtime scope": 'inventory.runtimeScope?.measureEnd||16' in character_js and 'note.measure>=startMeasure&&note.measure<=endMeasure' in character_js,
    "character assets preload": 'await Promise.all(sources.map(loadImage))' in character_js and 'character-ready' in character_js,
    "three phase flipbook motion": 'runtimePhaseFrameMap' in character_js and 'phaseFor(g,time)' in character_js and '"prep"' in character_js and '"rebound"' in character_js,
    "separate instrument effect layer": 'id="effectLayer"' in html and 'id="effectPrimary"' in html and '.effect-layer{' in css and 'triggerEffect(g,phase)' in character_js,
    "non-rapid hit returns neutral": 'rapidRepeatMaxGapSeconds' in character_js and 'nextGap>rapidMaxGap' in character_js and 'phase==="neutral"' in character_js,
    "rapid repeated hit keeps follow-through": 'keyFor(previous)===keyFor(next)' in character_js and 'return previous' in character_js,
}

failed=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items():
    print(("PASS" if ok else "FAIL"), name)
if failed:
    raise SystemExit("UI contract failures: "+", ".join(failed))
print(f"PASS all {len(checks)} UI contract checks")
