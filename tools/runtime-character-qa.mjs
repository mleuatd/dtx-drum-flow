import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const PUBLIC_URL=process.env.PUBLIC_URL||"https://mleuatd.github.io/dtx-drum-flow/";
const EXPECTED_SHA=process.env.GITHUB_SHA||"";
const RUN_ID=process.env.GITHUB_RUN_ID||"local";
const M0=Number(process.env.MEASURE_START||18), M1=Number(process.env.MEASURE_END||24);
const ROOT="qa-artifacts";
const TARGETS=(process.env.QA_ACTIONS||"BD+RD:RF/R,RD+SN:R/L,BD+HH:RF/R,HH+SN:R/L").split(",").filter(Boolean);
const viewports=[{name:"pc",width:1280,height:900},{name:"xperia-portrait",width:384,height:864}];
const readJson=async p=>JSON.parse(await fs.readFile(p,"utf8"));
const chart=await readJson("site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json");
const limbs=await readJson("site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json");
const inv=await readJson("character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json");
const limbMap=new Map((limbs.assignments||[]).map(x=>[`${Number(x.time).toFixed(6)}|${x.part}`,x.limb]));
const notes=(chart.notes||[]).filter(n=>n.measure>=M0&&n.measure<=M1).map(n=>({...n,limb:limbMap.get(`${Number(n.time).toFixed(6)}|${n.part}`)||n.limb}));
const groups=[]; for(const n of notes){const g=groups.at(-1);if(g&&Math.abs(n.time-g[0].time)<=.008)g.push(n);else groups.push([n]);}
const exactKey=g=>{const a=[...g].sort((x,y)=>x.part.localeCompare(y.part));return a.length>1?a.map(n=>n.part).join("+")+":"+a.map(n=>n.limb).join("/"):a[0].part+":"+a[0].limb};
const keyFor=g=>{const exact=exactKey(g);if(inv.runtimeFrameMap?.[exact])return exact;const parts=[...new Set(g.map(n=>n.part))].sort();const wildcard=parts.join("+")+":*";return inv.runtimeFrameMap?.[wildcard]?wildcard:exact};
const candidates=groups.map((g,i)=>({g,i,key:keyFor(g),time:Number(g[0].time),measure:g[0].measure,next:groups[i+1]?.[0]?.time??Infinity}));
const wanted=[...new Set(TARGETS)];
const selected=[];
for(const key of wanted){const list=candidates.filter(x=>x.key===key);if(!list.length)continue;selected.push([...list].sort((a,b)=>(b.next-b.time)-(a.next-a.time))[0]);}
for(const t of TARGETS)if(!selected.some(x=>x.key===t))throw new Error(`required action missing in measure range ${M0}-${M1}: ${t}`);
const timing=inv.motionTiming||{}, baseHit=Number(timing.hitEndSeconds??.09), baseRebound=Number(timing.reboundEndSeconds??.17);
function phaseTimes(ev){
  const gap=Math.max(0,ev.next-ev.time);
  let hit=baseHit,rebound=baseRebound;
  if(Number.isFinite(gap)&&gap<baseRebound){
    hit=Math.min(baseHit,Math.max(.045,gap*.52));
    rebound=Math.min(baseRebound,Math.max(hit+.016,gap-.006));
  }
  const out={hit:ev.time+.012};
  const reboundAt=ev.time+hit+(rebound-hit)*.48;
  const neutralAt=ev.time+rebound+.012;
  const margin=.006;
  if(!Number.isFinite(ev.next)||reboundAt<ev.next-margin) out.rebound=reboundAt;
  if(!Number.isFinite(ev.next)||neutralAt<ev.next-margin) out.neutral=neutralAt;
  return out;
}
function expectedFrame(key,phase){if(phase==="neutral")return inv.requiredFrames?.neutral?.path||"layers/character/base/neutral.png";const id=inv.runtimePhaseFrameMap?.[key]?.[phase]||inv.runtimeFrameMap?.[key];return inv.requiredFrames?.[id]?.path||"";}
async function deploymentContainsExpected(observed){
  if(!EXPECTED_SHA||observed===EXPECTED_SHA)return true;
  if(!observed)return false;
  try{
    const repo=process.env.GITHUB_REPOSITORY||"mleuatd/dtx-drum-flow";
    const r=await fetch(`https://api.github.com/repos/${repo}/compare/${EXPECTED_SHA}...${observed}`,{headers:{"Accept":"application/vnd.github+json"}});
    if(!r.ok)return false;
    const j=await r.json();
    return j.status==="ahead"||j.status==="identical";
  }catch{return false;}
}
async function waitForDeployment(){const deadline=Date.now()+12*60*1000;let last="";while(Date.now()<deadline){try{const r=await fetch(new URL("build.json?ts="+Date.now(),PUBLIC_URL),{cache:"no-store"});if(r.ok){const j=await r.json();last=j.commitSha||"";if(await deploymentContainsExpected(last))return {...j,expectedCommitSha:EXPECTED_SHA,acceptedDeploymentSha:last};}}catch{}await new Promise(r=>setTimeout(r,10000));}throw new Error(`Pages deployment timeout: expected-or-descendant-of=${EXPECTED_SHA} observed=${last}`);}
await fs.mkdir(ROOT,{recursive:true}); const deployment=await waitForDeployment();
const browser=await chromium.launch({headless:true}); const records=[]; let failed=0;
for(const vp of viewports){const context=await browser.newContext({viewport:{width:vp.width,height:vp.height}});const page=await context.newPage();const consoleErrors=[],pageErrors=[],failedRequests=[];
page.on("console",m=>{if(m.type()==="error")consoleErrors.push(m.text())});page.on("pageerror",e=>pageErrors.push(String(e)));page.on("requestfailed",r=>failedRequests.push(r.url()+" :: "+(r.failure()?.errorText||"failed")));page.on("response",r=>{if(r.status()>=400)failedRequests.push(r.status()+" "+r.url())});
for(let initAttempt=1;initAttempt<=3;initAttempt++){try{await page.goto(PUBLIC_URL+"?qa=1&initAttempt="+initAttempt,{waitUntil:"networkidle",timeout:120000});await page.waitForFunction(()=>window.__DTX_APP_READY__===true,null,{timeout:45000});await page.waitForFunction(()=>window.__DTX_CHARACTER_QA__?.snapshot().state?.startsWith("ready"),null,{timeout:45000});break;}catch(e){if(initAttempt===3)throw e;await page.waitForTimeout(1500);}}
const dir=path.join(ROOT,vp.name);await fs.mkdir(dir,{recursive:true});
for(const ev of selected){for(const [phase,t] of Object.entries(phaseTimes(ev))){await page.evaluate(time=>{const el=document.getElementById("timeline");el.value=String(time);el.dispatchEvent(new Event("input",{bubbles:true}))},t);await page.waitForTimeout(140);const actual=await page.evaluate(()=>window.__DTX_CHARACTER_QA__.snapshot());const expPhase=phase,expKey=phase==="neutral"?"neutral":ev.key,expFrame=expectedFrame(ev.key,phase);const charOk=actual.character.complete&&actual.character.naturalWidth>0&&actual.character.naturalHeight>0;const drumOk=actual.drum.complete&&actual.drum.naturalWidth>0&&actual.drum.naturalHeight>0&&/drum_base\.png/.test(actual.drum.src);const overlapped=(phase==="rebound"&&actual.animationKey!==ev.key&&actual.animationKey!=="neutral")||(phase==="neutral"&&actual.animationKey!=="neutral");const pass=!overlapped&&actual.phase===expPhase&&actual.animationKey===expKey&&actual.frame===expFrame&&charOk&&drumOk&&!actual.assetWarning&&!actual.initError;const safe=ev.key.replace(/[^A-Za-z0-9]+/g,"_");const shot=path.join(vp.name,`m${ev.measure}_${safe}_${phase}.png`);await page.locator(".stage").screenshot({path:path.join(ROOT,shot)});if(!pass&&!overlapped)failed++;records.push({commitSha:EXPECTED_SHA,deploymentPublicUrl:PUBLIC_URL,workflowRunId:RUN_ID,testedAt:new Date().toISOString(),browser:"chromium",viewport:vp,measure:ev.measure,testedTime:t,expectedActionKey:expKey,actualActionKey:actual.animationKey,expectedPhase:expPhase,actualPhase:actual.phase,expectedFrame:expFrame,actualFrame:actual.frame,limbs:actual.limbs,characterImageLoad:{ok:charOk,...actual.character},drumImageLoad:{ok:drumOk,...actual.drum},runtimeScope:actual.runtimeScope,assetWarning:actual.assetWarning,initError:actual.initError,consoleErrors:[...consoleErrors],pageErrors:[...pageErrors],failedRequests:[...failedRequests],screenshotPath:shot,status:overlapped?"SKIP_OVERLAPPED":pass?"PASS":"FAIL"});}}
await context.close();}
await browser.close();const summary={commitSha:EXPECTED_SHA,deployment,publicUrl:PUBLIC_URL,workflowRunId:RUN_ID,measureRange:[M0,M1],selectedActions:selected.map(x=>({measure:x.measure,time:x.time,key:x.key})),testedAt:new Date().toISOString(),failed,passed:records.length-failed,records};await fs.writeFile(path.join(ROOT,"runtime-qa.json"),JSON.stringify(summary,null,2));if(failed)process.exitCode=1;
