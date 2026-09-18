import fs from "node:fs/promises";
const file=process.argv[2]||"character-assets/prototypes/luna_say_maybe_16m/ACTIVE_PIPELINE_SESSION.json";
const s=JSON.parse(await fs.readFile(file,"utf8"));const used=new Set((s.completionEvidence||[]).map(x=>x.tool));
const missing=(s.requiredTools||[]).filter(x=>!used.has(x));
const ok=!missing.length||s.manualOverride;
const out={session:file,taskCategory:s.taskCategory,required:s.requiredTools||[],used:[...used],missing,manualOverride:s.manualOverride||null,compliant:ok};
console.log(JSON.stringify(out,null,2));if(!ok)process.exitCode=2;