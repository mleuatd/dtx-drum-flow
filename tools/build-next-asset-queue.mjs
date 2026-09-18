import fs from "node:fs/promises";
const base="character-assets/prototypes/luna_say_maybe_16m";
const read=async p=>JSON.parse(await fs.readFile(p,"utf8"));
const plan=await read(base+"/FULL_SONG_ASSET_IMPLEMENTATION_PLAN.json");
const blockPlan=await read(base+"/FULL_SONG_IMPLEMENTATION_BLOCK_PLAN.json");
const state=await read(base+"/CURRENT_PROJECT_STATE.json");
const blocks=blockPlan.blocks;
const blockFor=m=>blocks.find(b=>m>=b.measureStart&&m<=b.measureEnd)?.blockId||null;
const rank=a=>a.actionKey==="RC+SN:R/L"?0:(a.firstMeasure<=24?1:a.count>=100?2:a.count>=20?3:4);
const actions=plan.actions.filter(a=>["BLOCKED","NEW_IMAGE_REQUIRED"].includes(a.classification)).sort((a,b)=>rank(a)-rank(b)||a.firstMeasure-b.firstMeasure||b.count-a.count||a.actionKey.localeCompare(b.actionKey));
const items=[];
for(const a of actions){for(const phase of ["hit","rebound"]){items.push({
 id:"ASSETQ-"+String(items.length+1).padStart(3,"0"),actionKey:a.actionKey,phase,block:blockFor(a.firstMeasure),firstMeasure:a.firstMeasure,occurrenceCount:a.count,
 priority:a.actionKey==="RC+SN:R/L"?"P0":a.firstMeasure<=24?"P1":a.count>=100?"P1":a.count>=20?"P2":"P3",
 dependency:a.actionKey==="RC+SN:R/L"?"Blocks live runtime expansion beyond M8; must finish before later public runtime.":"Earlier contiguous measures must be complete before public runtime reaches this action.",
 currentAssetStatus:a.classification,reason:a.actionKey==="RC+SN:R/L"?"Immediate M9-16 blocker; corrected pair does not exist.":"Missing formal "+phase+"; first M"+a.firstMeasure+", occurrences "+a.count,
 nextAfterCompletion:null,status:a.actionKey==="RC+SN:R/L"?"BLOCKED_IMAGE_GENERATION_REQUIRED":"TODO"
});}}
for(let i=0;i<items.length;i++)items[i].nextAfterCompletion=items[i+1]?.id||"QUEUE_COMPLETE";
const out={schemaVersion:1,generatedAt:new Date().toISOString(),policy:{ordering:"blocking dependency -> first measure -> high occurrence -> actionKey; hit before rebound",liveRuntimeScope:state.liveRuntimeScope},nextItem:items.find(x=>!["DONE","SKIPPED"].includes(x.status))||null,items};
const dest=process.argv[2]||base+"/NEXT_ASSET_QUEUE.generated.json";
await fs.writeFile(dest,JSON.stringify(out,null,2)+"\n");
console.log(JSON.stringify({dest,next:out.nextItem,total:items.length},null,2));