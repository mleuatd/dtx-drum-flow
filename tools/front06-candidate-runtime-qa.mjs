import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";
const PUBLIC_URL=process.env.PUBLIC_URL||"http://127.0.0.1:4173/";
const TARGET="BD+RC:RF/R";
const ROOT="qa-artifacts/front06-runtime";
const readJson=async p=>JSON.parse(await fs.readFile(p,"utf8"));
const chart=await readJson("site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json");
const limbs=await readJson("site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json");
const inv=await readJson("character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json");
const limbMap=new Map((limbs.assignments||[]).map(x=>[`${Number(x.time).toFixed(6)}|${x.part}`,x.limb]));
const scope=inv.runtimeScope||{},m0=Number(scope.measureStart??1),m1=Number(scope.measureEnd??999);
const notes=(chart.notes||[]).filter(n=>n.measure>=m0&&n.measure<=m1).map(n=>({...n,limb:limbMap.get(`${Number(n.time).toFixed(6)}|${n.part}`)||n.limb}));
const groups=[];for(const n of notes){const g=groups.at(-1);if(g&&Math.abs(Number(n.time)-Number(g[0].time))<=.008)g.push(n);else groups.push([n]);}
const exactKey=g=>{const a=[...g].sort((x,y)=>x.part.localeCompare(y.part));return a.length>1?a.map(n=>n.part).join("+")+":"+a.map(n=>n.limb).join("/"):a[0].part+":"+a[0].limb};
const keyFor=g=>{const exact=exactKey(g);if(inv.runtimeFrameMap?.[exact])return exact;const parts=[...new Set(g.map(n=>n.part))].sort();const wildcard=parts.join("+")+":*";return inv.runtimeFrameMap?.[wildcard]?wildcard:exact};
const events=groups.map((g,i)=>({g,i,key:keyFor(g),time:Number(g[0].time),measure:g[0].measure,prev:Number(groups[i-1]?.[0]?.time??-Infinity),next:Number(groups[i+1]?.[0]?.time??Infinity)}));
const timing=inv.motionTiming||{},hitEnd=Number(timing.hitEndSeconds??.09),reboundEnd=Number(timing.reboundEndSeconds??.17);
const targetEvents=events.filter(x=>x.key===TARGET).map(x=>({...x,prevGap:x.time-x.prev,nextGap:x.next-x.time}));
if(!targetEvents.length)throw new Error("real chart target missing: "+TARGET);
targetEvents.sort((a,b)=>b.nextGap-a.nextGap);
const ev=targetEvents.find(x=>x.nextGap>reboundEnd+.018);
if(!ev)throw new Error(`no real-chart occurrence has enough post-hit gap for rebound/neutral: ${TARGET}`);
const before=ev.time-.012,hit=ev.time+.012,rebound=ev.time+hitEnd+(reboundEnd-hitEnd)*.48,after=ev.time+reboundEnd+.012;
const phaseForEvent=(e,time)=>{const delta=time-e.time;if(delta<0)return "neutral";const gap=Math.max(0,e.next-e.time);let h=hitEnd,r=reboundEnd;if(Number.isFinite(gap)&&gap<reboundEnd){h=Math.min(hitEnd,Math.max(.055,gap*.65));r=Math.min(reboundEnd,Math.max(h+.02,gap-.004));}if(delta<h)return "hit";if(delta<r)return "rebound";return "neutral";};
const expectedAt=time=>{let e=null;for(const x of events){if(x.time<=time)e=x;else break;}if(!e)return {key:"neutral",phase:"neutral"};const phase=phaseForEvent(e,time);return phase==="neutral"?{key:"neutral",phase}:{key:e.key,phase};};
const expectedFrame=(key,phase)=>{if(phase==="neutral")return inv.requiredFrames?.neutral?.path||"layers/character/base/neutral.png";const id=inv.runtimePhaseFrameMap?.[key]?.[phase]||inv.runtimeFrameMap?.[key];return inv.requiredFrames?.[id]?.path||"";};
const points=[["before_neighbor",before],["hit",hit],["rebound",rebound],["neutral_after",after]].map(([label,time])=>{const x=expectedAt(time);return {label,time,...x,frame:expectedFrame(x.key,x.phase)};});
await fs.mkdir(ROOT,{recursive:true});
const browser=await chromium.launch({headless:true});const records=[];let failed=0;
for(const vp of [{name:"pc",width:1280,height:900},{name:"xperia-portrait",width:384,height:864}]){
 const context=await browser.newContext({viewport:{width:vp.width,height:vp.height}}),page=await context.newPage();
 const consoleErrors=[],pageErrors=[],failedRequests=[];
 page.on("console",m=>{if(m.type()==="error")consoleErrors.push(m.text())});page.on("pageerror",e=>pageErrors.push(String(e)));page.on("requestfailed",r=>failedRequests.push(r.url()+" :: "+(r.failure()?.errorText||"failed")));page.on("response",r=>{if(r.status()>=400)failedRequests.push(r.status()+" "+r.url())});
 await page.goto(PUBLIC_URL+"?qa=1&front06=1",{waitUntil:"networkidle",timeout:120000});await page.waitForFunction(()=>window.__DTX_APP_READY__===true,null,{timeout:45000});await page.waitForFunction(()=>window.__DTX_CHARACTER_QA__?.snapshot().ready===true,null,{timeout:45000});
 for(const p of points){await page.evaluate(time=>{const el=document.getElementById("timeline");el.value=String(time);el.dispatchEvent(new Event("input",{bubbles:true}))},p.time);await page.waitForTimeout(180);const a=await page.evaluate(()=>window.__DTX_CHARACTER_QA__.snapshot());const charOk=a.character.complete&&a.character.naturalWidth>0&&a.character.naturalHeight>0,drumOk=a.drum.complete&&a.drum.naturalWidth>0&&a.drum.naturalHeight>0&&/drum_base\.png/.test(a.drum.src),ok=a.animationKey===p.key&&a.phase===p.phase&&a.frame===p.frame&&charOk&&drumOk&&!a.assetWarning&&!a.initError&&consoleErrors.length===0&&pageErrors.length===0&&failedRequests.length===0;if(!ok)failed++;const shot=path.join(ROOT,`${vp.name}_m${ev.measure}_${p.label}.png`);await page.locator(".stage").screenshot({path:shot});records.push({viewport:vp.name,target:TARGET,realChartMeasure:ev.measure,realChartEventTime:ev.time,prevGap:ev.prevGap,nextGap:ev.nextGap,label:p.label,testedTime:p.time,expectedKey:p.key,actualKey:a.animationKey,expectedPhase:p.phase,actualPhase:a.phase,expectedFrame:p.frame,actualFrame:a.frame,characterImageLoad:{ok:charOk,...a.character},drumImageLoad:{ok:drumOk,...a.drum},assetWarning:a.assetWarning,initError:a.initError,consoleErrors:[...consoleErrors],pageErrors:[...pageErrors],failedRequests:[...failedRequests],status:ok?"PASS":"FAIL",screenshotPath:shot});}
 await context.close();
}
await browser.close();
const report={schemaVersion:1,issueId:"MOTION-002",actionKey:TARGET,claimBatch:"HOLD-REPAIR-FRONT-06",source:"real Luna say maybe chart occurrence only",syntheticActionGeneration:false,selectedOccurrence:{measure:ev.measure,time:ev.time,prevGap:ev.prevGap,nextGap:ev.nextGap},sequence:"preceding real-chart state -> real-chart hit -> rebound -> neutral",viewports:["pc 1280x900","xperia-portrait 384x864"],failed,passed:records.length-failed,records};
await fs.writeFile(path.join(ROOT,"runtime-qa.json"),JSON.stringify(report,null,2));if(failed)process.exit(1);
