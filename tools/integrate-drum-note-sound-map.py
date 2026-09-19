from pathlib import Path

p=Path('site/app.js')
s=p.read_text(encoding='utf-8')
imp='import {applyDrumVoice} from "./drum-note-sound-map.js";\n'
if imp not in s:
    marker='import {LiveDrumEngine} from "./live-drum-engine.js";\n'
    if marker not in s: raise SystemExit('LiveDrumEngine import marker missing')
    s=s.replace(marker,marker+imp,1)
old='''  const t=Math.max(audioCtx.currentTime+.002,when??audioCtx.currentTime+.002);\n  liveDrumEngine.trigger(part,vel,t,note||{});'''
new='''  const t=Math.max(audioCtx.currentTime+.002,when??audioCtx.currentTime+.002);\n  const mapped=applyDrumVoice(note||{},part);\n  liveDrumEngine.trigger(mapped.part,vel,t,mapped.note);'''
if old not in s:
    if new in s:
        print('already integrated')
        raise SystemExit(0)
    raise SystemExit('drumAt integration marker missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('integrated drum note sound map')
