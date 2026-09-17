from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
html=(root/"site/index.html").read_text(encoding="utf-8")
js=(root/"site/app.js").read_text(encoding="utf-8")
parsers=(root/"site/parsers.js").read_text(encoding="utf-8")
css=(root/"site/styles.css").read_text(encoding="utf-8")
character_js=(root/"site/character-prototype.js").read_text(encoding="utf-8")
checks={
"11 drum lanes":'const PARTS=["LB","LC","HH","LP","SN","BD","HT","LT","FT","RD","RC"]' in js,
"song selection combobox":'id="songSelect"' in html,
"note speed range":re.search(r'id="noteSpeed"[^>]*min="0\.5"[^>]*max="8"[^>]*value="1"[^>]*step="0\.1"',html) is not None,
"Xperia viewport":'viewport-fit=cover' in html and 'user-scalable=no' in html,
"character canvas stays transparent":'if(!isLuna){ctx.fillStyle="#0e172a";ctx.fillRect(0,0,w,h)}' in js and 'background:transparent' in css,
"prototype runtime scope 1-4":'const PROTOTYPE_MEASURE_START=1' in character_js and 'const PROTOTYPE_MEASURE_END=4' in character_js,
"precomputed limb mapping":'Luna_say_maybe_1_16_limbs.json' in character_js and 'if(note?.limb)return note.limb' in character_js,
"m1-4 parapara character runtime":'runtimeFrameMap' in character_js and 'runtimePhaseFrameMap' in character_js and 'Object.values(data.frames).map(frame=>ASSET_ROOT+"/"+frame.path)' in character_js and 'Promise.allSettled(sources.map(loadImage))' in character_js,
"effect layer retained":'id="effectLayer"' in html and 'triggerEffect(g,phase)' in character_js,
}
failed=[n for n,ok in checks.items() if not ok]
for n,ok in checks.items(): print(("PASS" if ok else "FAIL"),n)
if failed: raise SystemExit("UI contract failures: "+", ".join(failed))
print(f"PASS all {len(checks)} UI contract checks")
