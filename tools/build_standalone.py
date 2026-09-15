from pathlib import Path
import json, re

root=Path(".")
index=(root/"site/index.html").read_text(encoding="utf-8")
css=(root/"site/styles.css").read_text(encoding="utf-8")
parsers=(root/"site/parsers.js").read_text(encoding="utf-8")
audio=(root/"site/audio-analysis.js").read_text(encoding="utf-8")
original_audio=(root/"site/original-audio.js").read_text(encoding="utf-8")
app=(root/"site/app.js").read_text(encoding="utf-8")
luna=json.loads((root/"site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json").read_text(encoding="utf-8"))
kana=json.loads((root/"site/charts/kanaetai_koto_bakari/Kanaetai_koto_bakari_FINAL_notes.json").read_text(encoding="utf-8"))

parsers=re.sub(r'\bexport\s+','',parsers)
audio=re.sub(r'\bexport\s+','',audio)
app=re.sub(r'^import .*?;\s*$','',app,flags=re.M)

fetch_code='const res=await fetch(path,{cache:"no-store"});if(!res.ok)throw new Error("完成譜面を取得できませんでした (HTTP "+res.status+")");const data=await res.json(),file=new File([JSON.stringify(data)],fileName,{type:"application/json"});'
embedded_code='const data=path.includes("kanaetai_koto_bakari")?KANAETAI_CHART:LUNA_CHART,file=new File([JSON.stringify(data)],fileName,{type:"application/json"});'
if fetch_code not in app:
    raise SystemExit("preset fetch block not found")
app=app.replace(fetch_code,embedded_code)

index=index.replace('<link rel="stylesheet" href="./styles.css">',f'<style>\n{css}\n</style>')
bundle=(
    'const LUNA_CHART='+json.dumps(luna,ensure_ascii=False,separators=(",",":"))+';\n'
    +'const KANAETAI_CHART='+json.dumps(kana,ensure_ascii=False,separators=(",",":"))+';\n'
    +parsers+'\n'+audio+'\n'+app+'\n'+original_audio
)
index=index.replace('<script type="module" src="./app.js"></script>',f'<script>\n{bundle}\n</script>')
index=index.replace('<script type="module" src="./original-audio.js"></script>','')

out=root/"dist"
out.mkdir(exist_ok=True)
(out/"DTX_Drum_Flow_Latest.html").write_text(index,encoding="utf-8")
print((out/"DTX_Drum_Flow_Latest.html").stat().st_size)
