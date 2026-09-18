import fs from "node:fs/promises";import crypto from "node:crypto";
const base="character-assets/prototypes/luna_say_maybe_16m";const start=Number(process.argv[2]||1),end=Number(process.argv[3]||148);
const read=async p=>JSON.parse(await fs.readFile(p,"utf8"));const chart=await read("site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json");const limbs=await read("site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json");const map=await read(base+"/ACTION_KEY_ASSET_MAP.json");
const lm=new Map(limbs.assignments.map(a=>[Number(a.time).toFixed(6)+"|"+a.part,a.limb]));const notes=chart.notes.filter(n=>n.measure>=start&&n.measure<=end).map(n=>({...n,limb:lm.get(Number(n.time).toFixed(6)+"|"+n.part)}));
const groups=[];for(const n of notes){const g=groups.at(-1);if(g&&Math.abs(g[0].time-n.time)<=.008)g.push(n);else groups.push([n]);}
const key=g=>{const a=[...g].sort((x,y)=>x.part.localeCompare(y.part));return a.length===1?a[0].part+":"+a[0].limb:a.map(x=>x.part).join("+")+":"+a.map(x=>x.limb).join("/")};
const parts=k=>k.split(":")[0].split("+");const limbsOf=k=>k.split(":")[1].split("/");
const cym=new Set(["LC","HH","RC","RD"]), tom=new Set(["HT","LT","FT"]);
function risk(i){const cur=groups[i],prev=groups[i-1],next=groups[i+1],ck=key(cur),pk=prev?key(prev):null,nk=next?key(next):null;let score=0;const reasons=[];const gapPrev=prev?cur[0].time-prev[0].time:null,gapNext=next?next[0].time-cur[0].time:null;
 if(gapPrev!=null&&gapPrev<.10){score+=3;reasons.push("very-short-prev-gap")} if(gapNext!=null&&gapNext<.10){score+=3;reasons.push("very-short-next-gap")}
 if(prev&&parts(pk).length!==parts(ck).length){score+=2;reasons.push("single-combo-change")}
 if(next&&parts(nk).length!==parts(ck).length){score+=2;reasons.push("combo-single-change")}
 const cp=parts(ck), pp=pk?parts(pk):[], np=nk?parts(nk):[];
 if((pp.some(x=>cym.has(x))&&cp.includes("SN"))||(cp.some(x=>cym.has(x))&&np.includes("SN"))){score+=2;reasons.push("cymbal-snare-transition")}
 if((pp.some(x=>tom.has(x))&&cp.some(x=>cym.has(x)))||(cp.some(x=>tom.has(x))&&np.some(x=>cym.has(x)))){score+=2;reasons.push("tom-cymbal-transition")}
 if(prev&&JSON.stringify(limbsOf(pk))!==JSON.stringify(limbsOf(ck))){score+=1;reasons.push("limb-pattern-change")}
 const entry=map.entries.find(e=>e.actionKey===ck);if(entry?.classification==="BLOCKED"){score+=5;reasons.push("blocked-asset")}
 const neighborBlocked=[pk,nk].filter(Boolean).some(k=>map.entries.find(e=>e.actionKey===k)?.classification==="BLOCKED");if(neighborBlocked){score+=4;reasons.push("blocked-asset-adjacency")}
 return {score,reasons,gapPrev,gapNext,previousKey:pk,currentKey:ck,nextKey:nk};}
const records=groups.map((g,i)=>({index:i,measure:g[0].measure,time:g[0].time,...risk(i)}));
const by=new Map();for(const r of records){(by.get(r.currentKey)||by.set(r.currentKey,[]).get(r.currentKey)).push(r)}
const selected=[];for(const [k,arr] of by){const add=new Map();const put=(r,why)=>{if(r)add.set(r.index,{...r,sampleReason:[...(add.get(r.index)?.sampleReason||[]),why]})};put(arr[0],"first");put(arr[Math.floor(arr.length/2)],"middle");put(arr.at(-1),"last");put([...arr].sort((a,b)=>(a.gapNext??999)-(b.gapNext??999))[0],"shortest-gap");put([...arr].sort((a,b)=>(b.gapNext??-1)-(a.gapNext??-1))[0],"longest-gap");for(const r of arr.filter(x=>x.score>=4))put(r,"high-risk");for(const r of arr.filter(x=>x.measure===start||x.measure===end))put(r,"block-boundary");selected.push(...add.values())}
const slug=s=>{const clean=s.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_|_$/g,"").slice(0,40);return clean+"_"+crypto.createHash("sha1").update(s).digest("hex").slice(0,7)};
for(const r of selected)r.screenshotNaming={measure:r.measure,time:r.time,previousSlug:slug(r.previousKey||"none"),currentSlug:slug(r.currentKey),nextSlug:slug(r.nextKey||"none")};
const out={schemaVersion:1,generatedAt:new Date().toISOString(),range:{start,end},riskRecords:records.sort((a,b)=>b.score-a.score||a.time-b.time),selectedSamples:selected.sort((a,b)=>a.time-b.time),policy:"Always include high-risk transitions; otherwise first/middle/last/shortest/longest/boundary."};
const dest=process.argv[4]||base+"/QA_SAMPLING_M"+start+"_"+end+".json";await fs.writeFile(dest,JSON.stringify(out,null,2)+"\n");console.log(JSON.stringify({dest,events:records.length,samples:selected.length,highRisk:records.filter(x=>x.score>=4).length},null,2));