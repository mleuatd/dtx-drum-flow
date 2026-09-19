import {chromium} from "playwright";import fs from "node:fs";fs.mkdirSync("qa/runtime-audio",{recursive:true});
const browser=await chromium.launch({headless:true,args:["--autoplay-policy=no-user-gesture-required"]});const page=await browser.newPage();
await page.route("**/*.flac",async route=>{await new Promise(r=>setTimeout(r,180));await route.continue()});
await page.goto("http://127.0.0.1:4173/?qa=cold-load",{waitUntil:"domcontentloaded"});
const r=await page.evaluate(async()=>{const m=await import("./live-drum-engine.js?cold="+Date.now()),ctx=new AudioContext(),out=ctx.createGain();out.connect(ctx.destination);await ctx.resume();const e=new m.LiveDrumEngine(ctx,out);let immediate=0;for(let i=0;i<24;i++){if(e.trigger(["BD","SN","HH","LC"][i%4],.82,ctx.currentTime+.02,{}))immediate++;await new Promise(r=>setTimeout(r,8))}await new Promise(r=>setTimeout(r,900));return{attempted:24,immediate,buffers:e.buffers.size,ready:e.ready}});
r.reproduced=r.immediate<r.attempted;fs.writeFileSync("qa/runtime-audio/cold-load-report.json",JSON.stringify(r,null,2));console.log(JSON.stringify(r,null,2));await browser.close();if(!r.reproduced)process.exit(1);
