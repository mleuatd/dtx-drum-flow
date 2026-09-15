from pathlib import Path
import json, re

root=Path(".")
index=(root/"site/index.html").read_text(encoding="utf-8")
css=(root/"site/styles.css").read_text(encoding="utf-8")
parsers=(root/"site/parsers.js").read_text(encoding="utf-8")
audio=(root/"site/audio-analysis.js").read_text(encoding="utf-8")
app=(root/"site/app.js").read_text(encoding="utf-8")
chart=json.loads((root/"site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json").read_text(encoding="utf-8"))

parsers=re.sub(r'\bexport\s+','',parsers)
audio=re.sub(r'\bexport\s+','',audio)
app=re.sub(r'^import .*?;\s*$','',app,flags=re.M)

old='''$("loadLuna").onclick=async()=>{\n  try{\n    setStatus("Luna say maybe 完成譜面を読み込んでいます…");\n    const res=await fetch("./charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json",{cache:"no-store"});\n    if(!res.ok)throw new Error("完成譜面を取得できませんでした");\n    const data=await res.json();\n    const file=new File([JSON.stringify(data)],"Luna_say_maybe_FINAL_notes.json",{type:"application/json"});\n    setChart(await parseChart(file));\n    setStatus("Luna say maybe 完成譜面（Songsterr基準・元音源+1.693秒同期）を読み込みました。元音源を開くと同期再生できます。");\n  }catch(err){\n    setStatus("Luna say maybe 完成譜面の読み込みに失敗しました: "+err.message);\n  }\n};'''
new='''$("loadLuna").onclick=async()=>{\n  try{\n    setStatus("Luna say maybe 完成譜面を読み込んでいます…");\n    const file=new File([JSON.stringify(LUNA_CHART)],"Luna_say_maybe_FINAL_notes.json",{type:"application/json"});\n    setChart(await parseChart(file));\n    setStatus("Luna say maybe 完成譜面（Songsterr基準・元音源+1.693秒同期）を読み込みました。元音源を開くと同期再生できます。");\n  }catch(err){\n    setStatus("Luna say maybe 完成譜面の読み込みに失敗しました: "+err.message);\n  }\n};'''
if old not in app:
    raise SystemExit("loadLuna block not found")
app=app.replace(old,new)

index=index.replace('<link rel="stylesheet" href="./styles.css">',f'<style>\n{css}\n</style>')
bundle='const LUNA_CHART='+json.dumps(chart,ensure_ascii=False,separators=(",",":"))+';\n'+parsers+'\n'+audio+'\n'+app
index=index.replace('<script type="module" src="./app.js"></script>',f'<script>\n{bundle}\n</script>')

out=root/"dist"
out.mkdir(exist_ok=True)
(out/"DTX_Drum_Flow_Latest.html").write_text(index,encoding="utf-8")
print((out/"DTX_Drum_Flow_Latest.html").stat().st_size)
