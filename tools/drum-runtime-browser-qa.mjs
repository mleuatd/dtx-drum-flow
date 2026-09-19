import { chromium } from "playwright";
import fs from "node:fs";
fs.mkdirSync("qa/runtime-audio",{recursive:true});
const browser=await chromium.launch({headless:true,args:["--autoplay-policy=no-user-gesture-required"]});
const page=await browser.newPage();
const errors=[];page.on("pageerror",e=>errors.push(String(e)));page.on("console",m=>{if(m.type()==="error"&&!m.text().includes("404"))errors.push(m.text())});
await page.goto("http://127.0.0.1:4173/?qa=runtime-audio",{waitUntil:"networkidle"});
const result=await page.evaluate(async()=>{
 const mod=await import("./live-drum-engine.js?qa="+Date.now());
 const ctx=new AudioContext({latencyHint:"interactive"}), out=ctx.createGain();out.connect(ctx.destination);
 const engine=new mod.LiveDrumEngine(ctx,out); await ctx.resume();
 const tests=[["BD",36],["SN",38],["HH",42],["HT",48],["LT",45],["FT",41],["RD",51],["LC",49],["RC",57],["LP",44]];
 const rows=[];
 for(const [part,gmNote] of tests){
   const before=engine.nodes.size; const node=engine.trigger(part,.82,ctx.currentTime+.03,{gmNote});
   await new Promise(r=>setTimeout(r,80));
   const activeSoon=engine.nodes.size;
   await new Promise(r=>setTimeout(r,420));
   rows.push({part,gmNote,before,activeSoon,after:engine.nodes.size,bufferCount:engine.buffers.size,nodeReturned:!!node});
 }
 await new Promise(r=>setTimeout(r,300));
 return {state:ctx.state,rows,buffers:engine.buffers.size,ready:engine.ready};
});
const report={...result,errors,status:(result.state==="running"&&result.buffers>=10&&result.rows.every(x=>x.bufferCount>0)&&result.rows.some(x=>x.activeSoon>0)&&errors.length===0)?"PASS":"FAIL"};
fs.writeFileSync("qa/runtime-audio/report.json",JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));await page.screenshot({path:"qa/runtime-audio/page.png",fullPage:true});await browser.close();
if(report.status!=="PASS")process.exit(1);
