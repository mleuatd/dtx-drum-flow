import { chromium } from "playwright";import fs from "node:fs";
fs.mkdirSync("qa/runtime-audio",{recursive:true});
const speeds=[.5,.6,.7,.8,.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2];
const browser=await chromium.launch({headless:true,args:["--autoplay-policy=no-user-gesture-required"]});const page=await browser.newPage();const errors=[];
page.on("pageerror",e=>errors.push(String(e)));page.on("console",m=>{if(m.type()==="error"&&!m.text().includes("404"))errors.push(m.text())});
await page.goto("http://127.0.0.1:4173/?qa=speed-load",{waitUntil:"networkidle"});
const result=await page.evaluate(async(speeds)=>{
 const mod=await import("./live-drum-engine.js?speedqa="+Date.now());const ctx=new AudioContext({latencyHint:"interactive"}),out=ctx.createGain();out.connect(ctx.destination);const e=new mod.LiveDrumEngine(ctx,out);await ctx.resume();
 const t0=performance.now();await e.preload();const preloadMs=performance.now()-t0,expected=e.buffers.size;
 const voices=[["BD",36],["SN",38],["HH",42],["HT",48],["LT",45],["FT",41],["RD",51],["LC",49],["RC",57],["LP",44]];
 const rows=[];
 for(const speed of speeds){let attempted=0,returned=0;const start=ctx.currentTime+.06,step=.125/speed;
  for(let i=0;i<64;i++){const [part,gmNote]=voices[i%voices.length];attempted++;if(e.trigger(part,.82,start+i*step,{gmNote}))returned++}
  await new Promise(r=>setTimeout(r,Math.max(180,64*step*1000+120)));rows.push({speed,attempted,returned,missedImmediate:attempted-returned,buffers:e.buffers.size,ready:e.ready});
  e.stop();
 }
 return {preloadMs,expected,rows,ready:e.ready,buffers:e.buffers.size};
},speeds);
const status=result.ready&&result.buffers===result.expected&&result.rows.every(r=>r.missedImmediate===0&&r.ready&&r.buffers===result.expected)&&errors.length===0?"PASS":"FAIL";
const report={purpose:"Verify full acoustic sample preload and no trigger misses from 0.5x through 2.0x under dense 16th-note scheduling",...result,errors,status};
fs.writeFileSync("qa/runtime-audio/speed-load-report.json",JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));await browser.close();if(status!=="PASS")process.exit(1);
