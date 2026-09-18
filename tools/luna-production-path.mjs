import fs from "node:fs/promises";
const base="character-assets/prototypes/luna_say_maybe_16m";const start=Number(process.argv[2]),end=Number(process.argv[3]);
if(!Number.isInteger(start)||!Number.isInteger(end)||start<1||end<start)throw new Error("usage: node tools/luna-production-path.mjs <start> <end> [out.json]");
const read=async p=>JSON.parse(await fs.readFile(p,"utf8"));const chart=await read("site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json");const limbs=await read("site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json");const map=await read(base+"/ACTION_KEY_ASSET_MAP.json");
const lm=new Map(limbs.assignments.map(a=>[Number(a.time).toFixed(6)+"|"+a.part,a.limb]));const notes=chart.notes.filter(n=>n.measure>=start&&n.measure<=end).map(n=>({...n,limb:lm.get(Number(n.time).toFixed(6)+"|"+n.part)}));const groups=[];for(const n of notes){const g=groups.at(-1);if(g&&Math.abs(g[0].time-n.time)<=.008)g.push(n);else groups.push([n])}
const key=g=>{const a=[...g].sort((x,y)=>x.part.localeCompare(y.part));return a.length===1?a[0].part+":"+a[0].limb:a.map(x=>x.part).join("+")+":"+a.map(x=>x.limb).join("/")};
const used=[...new Set(groups.map(key))],by=new Map(map.entries.map(e=>[e.actionKey,e])),entries=used.map(k=>by.get(k)||{actionKey:k,classification:"MISSING_MAPPING"});
const fullReasons=entries.filter(e=>e.classification!=="REUSE_APPROVED"||!e.runtimeMapped).map(e=>({actionKey:e.actionKey,classification:e.classification,runtimeMapped:e.runtimeMapped||false}));
const path=fullReasons.length?"FULL_PATH":"FAST_PATH";const out={schemaVersion:1,generatedAt:new Date().toISOString(),range:{start,end},path,actionKeys:used,fullPathReasons:fullReasons,
 fastPath:path==="FAST_PATH"?["chart/limb validation","mapping/rejected checks","runtime QA","PC/Xperia screenshots","regression"]:null,
 fullPath:path==="FULL_PATH"?["missing asset detection","generation queue","candidate QA","formal save gate","mapping","runtime QA","screenshot QA","regression","completion definition"]:null};
const dest=process.argv[4]||base+"/PRODUCTION_PATH_M"+start+"_"+end+".json";await fs.writeFile(dest,JSON.stringify(out,null,2)+"\n");console.log(JSON.stringify(out,null,2));