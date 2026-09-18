from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
html=(root/"site/index.html").read_text(encoding="utf-8")
js=(root/"site/app.js").read_text(encoding="utf-8")
parsers=(root/"site/parsers.js").read_text(encoding="utf-8")
css=(root/"site/styles.css").read_text(encoding="utf-8")
character_js=(root/"site/character-prototype.js").read_text(encoding="utf-8")
import json
inventory=json.loads((root/"character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json").read_text(encoding="utf-8"))
checks={
"11 drum lanes":'const PARTS=["LB","LC","HH","LP","SN","BD","HT","LT","FT","RD","RC"]' in js,
"song selection combobox":'id="songSelect"' in html,
"note speed range":re.search(r'id="noteSpeed"[^>]*min="0\.5"[^>]*max="8"[^>]*value="1"[^>]*step="0\.1"',html) is not None,
"Xperia viewport":'viewport-fit=cover' in html and 'user-scalable=no' in html,
"character canvas stays transparent":'if(!isLuna){ctx.fillStyle="#0e172a";ctx.fillRect(0,0,w,h)}' in js and 'background:transparent' in css,
"prototype runtime scope 1-8":inventory.get("runtimeScope",{}).get("measureStart")==1 and inventory.get("runtimeScope",{}).get("measureEnd")==8 and "inventory.runtimeScope?.measureStart" in character_js and "inventory.runtimeScope?.measureEnd" in character_js,
"precomputed limb mapping":'Luna_say_maybe_full_limbs.json' in character_js and 'if(note?.limb)return note.limb' in character_js,
"m1-8 parapara character runtime":'runtimeFrameMap' in character_js and 'runtimePhaseFrameMap' in character_js and 'Object.values(data.frames)' in character_js and 'Promise.allSettled' in character_js,
"effect layer retained":'id="effectLayer"' in html and 'triggerEffect(g,phase)' in character_js,
}
failed=[n for n,ok in checks.items() if not ok]
for n,ok in checks.items(): print(("PASS" if ok else "FAIL"),n)
if failed: raise SystemExit("UI contract failures: "+", ".join(failed))
print(f"PASS all {len(checks)} UI contract checks")
