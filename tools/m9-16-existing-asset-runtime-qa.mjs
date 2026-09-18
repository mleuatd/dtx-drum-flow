import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const URL="https://mleuatd.github.io/dtx-drum-flow/";
const inventoryPath="character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json";
const planPath="character-assets/prototypes/luna_say_maybe_16m/M9_16_RUNTIME_EXPANSION_PLAN.json";
const inventory=JSON.parse(await fs.readFile(inventoryPath,"utf8"));
const plan=JSON.parse(await fs.readFile(planPath,"utf8"));

const qaInventory=structuredClone(inventory);
qaInventory.runtimeScope=structuredClone(plan.targetRuntimeScope);
for(const [id,frame] of Object.entries(plan.requiredFramesToAdd)){
  if(id.startsWith("bd_sn_")) qaInventory.requiredFrames[id]=frame;
}
qaInventory.runtimeFrameMap["BD+SN:*"]="bd_sn_hit_refresh";
qaInventory.runtimePhaseFrameMap["BD+SN:*"]={prep:"neutral",hit:"bd_sn_hit_refresh",rebound:"bd_sn_rebound_refresh"};
qaInventory.runtimeFrameMap["RC+SN:*"]="neutral";
qaInventory.runtimePhaseFrameMap["RC+SN:*"]={prep:"neutral",hit:"neutral",rebound:"neutral"};

const allEvents=plan.m9_16QaEvents;
const events=allEvents.filter(e=>e.key!=="RC+SN:*");
const viewports=[
  {name:"pc",width:1280,height:900},
  {name:"xperia-portrait",width:384,height:864}
];

function samplesFor(index){
  const ev=allEvents[index];
  const next=allEvents[index+1];
  const gap=next?Math.max(0,next.time-ev.time):Infinity;
  const baseHitEnd=0.18,baseReboundEnd=0.28;
  let hitEnd=baseHitEnd,reboundEnd=baseReboundEnd;
  if(Number.isFinite(gap)&&gap<baseReboundEnd){
    hitEnd=Math.min(baseHitEnd,Math.max(.055,gap*.65));
    reboundEnd=Math.min(baseReboundEnd,Math.max(hitEnd+.02,gap-.004));
  }
  const hitOffset=Math.min(.03,Math.max(.012,hitEnd*.45));
  const reboundOffset=hitEnd+(reboundEnd-hitEnd)*.5;
  const postOffset=Number.isFinite(gap)
    ? Math.max(reboundEnd+.006,Math.min(gap+.012,baseReboundEnd+.03))
    : baseReboundEnd+.03;
  return [
    {name:"pre",offset:-.015},
    {name:"hit",offset:hitOffset},
    {name:"rebound",offset:reboundOffset},
    {name:"post",offset:postOffset}
  ];
}
function expectedFrame(key,phase){
  const phases=qaInventory.runtimePhaseFrameMap[key]||{};
  const id=phases[phase]||qaInventory.runtimeFrameMap[key]||"neutral";
  return qaInventory.requiredFrames[id]?.path||qaInventory.requiredFrames.neutral.path;
}
function keySafe(k){return k.replace(/[^A-Za-z0-9]+/g,"_");}

const browser=await chromium.launch({headless:true});
const outRoot="qa-artifacts-existing-m9-16";
await fs.mkdir(outRoot,{recursive:true});
const summary={
  url:URL,
  generatedAt:new Date().toISOString(),
  mode:"QA-only inventory interception; public runtime remains M1-8",
  targetScope:qaInventory.runtimeScope,
  rcSnPolicy:"RC+SN is mapped to neutral only to satisfy prototype initialization and is excluded from approval.",
  records:[],
  perKey:{},
  viewports:{}
};

for(const vp of viewports){
  const context=await browser.newContext({viewport:{width:vp.width,height:vp.height},deviceScaleFactor:1});
  const page=await context.newPage();
  const errors=[];
  page.on("console",m=>{if(m.type()==="error")errors.push("console: "+m.text());});
  page.on("pageerror",e=>errors.push("pageerror: "+String(e)));
  await page.route(/asset_inventory\.json(?:\?.*)?$/,async route=>{
    await route.fulfill({status:200,contentType:"application/json",body:JSON.stringify(qaInventory)});
  });
  await page.goto(URL,{waitUntil:"networkidle",timeout:120000});
  await page.waitForFunction(()=>window.__DTX_APP_READY__===true,{timeout:30000});
  await page.waitForFunction(()=>{
    const el=document.getElementById("characterBackdrop");
    return el&&el.classList.contains("character-ready")&&el.dataset.state;
  },{timeout:30000});

  const initial=await page.evaluate(()=>{
    const r=document.getElementById("characterBackdrop");
    return {state:r?.dataset.state||"",scope:r?.dataset.scope||"",noteCount:r?.dataset.noteCount||"",groupCount:r?.dataset.groupCount||"",assetIssue:r?.dataset.assetIssue||"",initError:r?.dataset.initError||""};
  });
  const dir=path.join(outRoot,vp.name);
  await fs.mkdir(dir,{recursive:true});

  for(let globalIndex=0;globalIndex<allEvents.length;globalIndex++){
    const ev=allEvents[globalIndex];
    if(ev.key==="RC+SN:*")continue;
    const prev=allEvents[globalIndex-1]||null;
    const next=allEvents[globalIndex+1]||null;
    const crossesMissingNeighbor=prev?.key==="RC+SN:*"||next?.key==="RC+SN:*";
    for(const sample of samplesFor(globalIndex)){
      const t=Math.max(0,ev.time+sample.offset);
      await page.evaluate(time=>{
        const timeline=document.getElementById("timeline");
        timeline.value=String(time);
        timeline.dispatchEvent(new Event("input",{bubbles:true}));
      },t);
      await page.waitForTimeout(110);
      const dom=await page.evaluate(()=>{
        const root=document.getElementById("characterBackdrop");
        const char=document.getElementById("characterLayer");
        const drum=document.getElementById("drumLayer");
        const rr=root.getBoundingClientRect(),cr=char.getBoundingClientRect(),dr=drum.getBoundingClientRect();
        return {
          frame:root.dataset.frame||"",
          phase:root.dataset.phase||"",
          animationKey:root.dataset.animationKey||"",
          limbs:root.dataset.limbs||"",
          state:root.dataset.state||"",
          assetIssue:root.dataset.assetIssue||"",
          initError:root.dataset.initError||"",
          character:{naturalWidth:char.naturalWidth,naturalHeight:char.naturalHeight,x:cr.x,y:cr.y,w:cr.width,h:cr.height},
          drum:{naturalWidth:drum.naturalWidth,naturalHeight:drum.naturalHeight,x:dr.x,y:dr.y,w:dr.width,h:dr.height},
          root:{x:rr.x,y:rr.y,w:rr.width,h:rr.height}
        };
      });
      const expected=(sample.name==="hit"||sample.name==="rebound")?expectedFrame(ev.key,sample.name):null;
      const keyMatch=(sample.name==="hit"||sample.name==="rebound")?dom.animationKey===ev.key:true;
      const frameMatch=expected?dom.frame===expected:true;
      const loadOk=dom.character.naturalWidth===1448&&dom.character.naturalHeight===1086&&dom.drum.naturalWidth===1448&&dom.drum.naturalHeight===1086;
      const noWarnings=!dom.assetIssue&&!dom.initError;
      const base=`${String(globalIndex+1).padStart(2,"0")}_m${ev.measure}_${ev.time.toFixed(6)}_${keySafe(ev.key)}_${sample.name}`;
      const shot=path.join(vp.name,base+".png");
      await page.locator(".stage").screenshot({path:path.join(outRoot,shot)});
      const rec={viewport:vp.name,event:ev,previous:prev,next,sample:sample.name,sampleTime:t,expectedFrame:expected,keyMatch,frameMatch,loadOk,noWarnings,crossesMissingNeighbor,dom,screenshot:shot};
      summary.records.push(rec);
      summary.perKey[ev.key]??={records:0,hitMismatches:0,reboundMismatches:0,loadFailures:0,warnings:0,measures:new Set(),times:new Set(),neighborBlocked:0,screenshots:[]};
      const agg=summary.perKey[ev.key];
      agg.records++;
      agg.measures.add(ev.measure); agg.times.add(ev.time); agg.screenshots.push(shot);
      if(sample.name==="hit"&&!frameMatch)agg.hitMismatches++;
      if(sample.name==="rebound"&&!frameMatch)agg.reboundMismatches++;
      if(!loadOk)agg.loadFailures++;
      if(!noWarnings)agg.warnings++;
      if(crossesMissingNeighbor)agg.neighborBlocked++;
    }
  }
  summary.viewports[vp.name]={initial,errors};
  await context.close();
}
for(const [key,v] of Object.entries(summary.perKey)){
  v.measures=[...v.measures].sort((a,b)=>a-b);
  v.times=[...v.times].sort((a,b)=>a-b);
}
await fs.writeFile(path.join(outRoot,"runtime-qa.json"),JSON.stringify(summary,null,2));
await browser.close();

const failures=[];
for(const [key,v] of Object.entries(summary.perKey)){
  if(v.hitMismatches||v.reboundMismatches||v.loadFailures||v.warnings)failures.push({key,...v});
}
for(const [vp,v] of Object.entries(summary.viewports)){
  if(v.errors.length||v.initial.assetIssue||v.initial.initError||v.initial.scope!=="1-16")failures.push({viewport:vp,...v});
}
if(failures.length){
  console.error(JSON.stringify(failures,null,2));
  process.exitCode=1;
}
