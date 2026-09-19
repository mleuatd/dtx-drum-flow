from pathlib import Path

path = Path("site/app.js")
text = path.read_text(encoding="utf-8")

import_line = 'import {LiveDrumEngine} from "./live-drum-engine.js";\n'
if import_line not in text:
    anchor = 'import {decodeAudio,analyzeOnsets,realignNotes} from "./audio-analysis.js";\n'
    if anchor not in text:
        raise SystemExit("audio-analysis import anchor missing")
    text = text.replace(anchor, anchor + import_line, 1)

old_decl = "audioCtx=null,drumBus=null,originalSource=null"
new_decl = "audioCtx=null,drumBus=null,liveDrumEngine=null,originalSource=null"
if old_decl in text:
    text = text.replace(old_decl, new_decl, 1)
elif new_decl not in text:
    raise SystemExit("audio state declaration anchor missing")

ensure_anchor = "  if(audioCtx.state===\"suspended\")await audioCtx.resume();\n"
ensure_insert = "  liveDrumEngine??=new LiveDrumEngine(audioCtx,drumBus);\n"
if ensure_insert not in text:
    if ensure_anchor not in text:
        raise SystemExit("ensureAudio anchor missing")
    text = text.replace(ensure_anchor, ensure_insert + ensure_anchor, 1)

old_stop = "function stopScheduled(){for(const n of scheduledNodes){try{n.stop()}catch{}}scheduledNodes=[]}"
new_stop = "function stopScheduled(){for(const n of scheduledNodes){try{n.stop()}catch{}}scheduledNodes=[];liveDrumEngine?.stop()}"
if old_stop in text:
    text = text.replace(old_stop, new_stop, 1)
elif new_stop not in text:
    raise SystemExit("stopScheduled anchor missing")

start = text.find("function drumAt(part,vel=.8,when=null,note=null){")
end = text.find("function stopOriginal()", start)
if start < 0 or end < 0:
    raise SystemExit("drumAt replacement markers missing")

adapter = '''function drumAt(part,vel=.8,when=null,note=null){
  if(!$("drumSound").checked||!audioCtx||!liveDrumEngine)return;
  const t=Math.max(audioCtx.currentTime+.002,when??audioCtx.currentTime+.002);
  liveDrumEngine.trigger(part,vel,t,note||{});
  setTimeout(()=>flash(part),Math.max(0,(t-audioCtx.currentTime)*1000));
}
'''
text = text[:start] + adapter + text[end:]
path.write_text(text, encoding="utf-8")
print("Integrated LiveDrumEngine into site/app.js")
