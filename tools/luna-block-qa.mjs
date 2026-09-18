import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const start=Number(process.env.MEASURE_START||"1");
const end=Number(process.env.MEASURE_END||"8");
const target=(process.env.ACTION_KEY||"").trim();
const url=process.env.PUBLIC_URL||"https://mleuatd.github.io/dtx-drum-flow/";
if(!Number.isInteger(start)||!Number.isInteger(end)||start<1||end<start)throw new Error("invalid measure range");

const read=async p=>JSON.parse(await fs.readFile(p,"utf8"));
const chart=await read("site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json");
const limb=await read("site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json");
const mapping=await read("character-assets/prototypes/luna_say_maybe_16m/ACTION_KEY_ASSET_MAP.json");
const inventory=await read("character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json");
const rejected=await read("character-assets/prototypes/luna_say_maybe_16m/REJECTED_ASSET_REGISTRY.json");
const manifest=await read("character-assets/config/assets_manifest.json");
const out="qa-artifacts-luna-block";
await fs.mkdir(out,{recursive:true});

const lm=new Map(limb.assignments.map(a=>[Number(a.time).toFixed(6)+"|"+a.part,a.limb]));
const scoped=chart.notes.filter(n=>n.measure>=start&&n.measure<=end).map(n=>({...n,limb:lm.get(Number(n.time).toFixed(6)+"|"+n.part)}));
const groups=[];
for(const n of scoped){const g=groups.at(-1);if(g&&Math.abs(n.time-g[0].time)<=.008)g.push(n);else groups.push([n]);}
const exactKey=g=>{const a=[...g].sort((x,y)=>x.part.localeCompare(y.part));return a.length===1?a[0].part+":"+a[0].limb:a.map(x=>x.part).join("+")+":"+a.map(x=>x.limb).join("/")};
const entries=new Map(mapping.entries.map(e=>[e.actionKey,e]));
const usedKeys=[...new Set(groups.map(exactKey))].filter(k=>!target||k===target);
const problems=[];
for(const k of usedKeys){
  const e=entries.get(k);
  if(!e){problems.push({key:k,reason:"missing mapping master entry"});continue;}
  if(["NEW_IMAGE_REQUIRED","BLOCKED","REJECTED_NEVER_USE"].includes(e.classification))problems.push({key:k,reason:"asset classification "+e.classification});
  if(!e.hitAsset||!e.reboundAsset)problems.push({key:k,reason:"missing hit/rebound formal asset"});
}
const denyPaths=new Set(rejected.entries.map(x=>x.githubPath).filter(Boolean));
for(const k of usedKeys){
  const e=entries.get(k); if(!e)continue;
  if(denyPaths.has(e.hitAsset)||denyPaths.has(e.reboundAsset))problems.push({key:k,reason:"rejected registry path"});
}
const summary={generatedAt:new Date().toISOString(),range:{start,end},targetActionKey:target||null,noteCount:scoped.length,groupCount:groups.length,actionKeys:usedKeys,staticProblems:problems,status:problems.length?"BLOCKED":"READY_FOR_BROWSER_QA",browser:null};
if(problems.length){
  await fs.writeFile(path.join(out,"summary.json"),JSON.stringify(summary,null,2));
  console.log(JSON.stringify(summary,null,2));
  process.exit(0);
}

const manifestByPath=new Map(manifest.assets.map(a=>[a.path,a]));
const qa=structuredClone(inventory);
qa.runtimeScope={measureStart:start,measureEnd:end,noteCount:scoped.length,groupCount:groups.length,firstNoteTime:scoped[0]?.time||0,lastNoteTime:scoped.at(-1)?.time||0,expectedKeys:[]};
qa.requiredFrames={neutral:inventory.requiredFrames.neutral};
qa.runtimeFrameMap={};
qa.runtimePhaseFrameMap={};
const id=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,"_").replace(/^_|_$/g,"");
for(const k of usedKeys){
  const e=entries.get(k);
  const rk=e.limbAwareRuntimeKey||e.runtimeKey;
  const hitId=id(k)+"_hit", rbId=id(k)+"_rebound";
  const hit=e.hitAsset, rb=e.reboundAsset;
  if(!manifestByPath.has(hit)||!manifestByPath.has(rb))throw new Error(k+": formal assets absent from manifest");
  qa.requiredFrames[hitId]={path:hit.replace(/^character-assets\//,""),state:"qa"};
  qa.requiredFrames[rbId]={path:rb.replace(/^character-assets\//,""),state:"qa"};
  qa.runtimeFrameMap[rk]=hitId;
  qa.runtimePhaseFrameMap[rk]={prep:"neutral",hit:hitId,rebound:rbId};
  qa.runtimeScope.expectedKeys.push(rk);
}
qa.runtimeScope.expectedKeys=[...new Set(qa.runtimeScope.expectedKeys)];

const browser=await chromium.launch({headless:true});
const results={};
for(const vp of [{name:"pc",width:1280,height:900},{name:"xperia",width:384,height:864}]){
  const context=await browser.newContext({viewport:{width:vp.width,height:vp.height}});
  const page=await context.newPage(); const errors=[];
  page.on("console",m=>{if(m.type()==="error")errors.push("console:"+m.text())});
  page.on("pageerror",e=>errors.push("pageerror:"+String(e)));
  await page.route(/asset_inventory\.json(?:\?.*)?$/,route=>route.fulfill({status:200,contentType:"application/json",body:JSON.stringify(qa)}));
  await page.goto(url,{waitUntil:"networkidle",timeout:120000});
  await page.waitForFunction(()=>window.__DTX_APP_READY__===true,{timeout:30000});
  const selected=[];
  for(const k of usedKeys){
    const ev=groups.filter(g=>exactKey(g)===k);
    const picks=ev.length<=3?ev:[ev[0],ev[Math.floor(ev.length/2)],ev.at(-1)];
    for(const g of picks)selected.push({key:k,time:g[0].time,measure:g[0].measure});
  }
  const records=[];
  for(const ev of selected){
    for(const s of [{phase:"pre",o:-.015},{phase:"hit",o:.03},{phase:"rebound",o:.22},{phase:"post",o:.31}]){
      const t=Math.max(0,ev.time+s.o);
      await page.evaluate(time=>{const x=document.getElementById("timeline");x.value=String(time);x.dispatchEvent(new Event("input",{bubbles:true}))},t);
      await page.waitForTimeout(100);
      const dom=await page.evaluate(()=>{const r=document.getElementById("characterBackdrop");return {frame:r?.dataset.frame||"",phase:r?.dataset.phase||"",key:r?.dataset.animationKey||"",limbs:r?.dataset.limbs||"",assetIssue:r?.dataset.assetIssue||"",initError:r?.dataset.initError||""}});
      const name=`${vp.name}_m${ev.measure}_${ev.time.toFixed(6)}_${id(ev.key)}_${s.phase}.png`;
      await page.locator(".stage").screenshot({path:path.join(out,name)});
      records.push({...ev,sample:s.phase,sampleTime:t,dom,screenshot:name});
    }
  }
  results[vp.name]={errors,records};
  await context.close();
}
await browser.close();
summary.browser=results;
const runtimeProblems=[];
for(const [vp,x] of Object.entries(results)){
  runtimeProblems.push(...x.errors.map(error=>({viewport:vp,error})));
  for(const r of x.records)if(r.dom.assetIssue||r.dom.initError)runtimeProblems.push({viewport:vp,record:r});
}
summary.runtimeProblems=runtimeProblems;
summary.status=runtimeProblems.length?"FAIL":"PASS_AUTOMATED_REQUIRES_VISUAL_SCREENSHOT_REVIEW";
await fs.writeFile(path.join(out,"summary.json"),JSON.stringify(summary,null,2));
console.log(JSON.stringify({status:summary.status,range:summary.range,keys:usedKeys,problems:runtimeProblems.length},null,2));
if(runtimeProblems.length)process.exitCode=1;
