// QA trigger: post SN:R rebound continuity fix 2026-09-18T12:41+09:00
import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const URL = "https://mleuatd.github.io/dtx-drum-flow/";
const events = [
  {time:4.714583,key:"SN:L",measure:1},
  {time:4.930410,key:"SN:R",measure:1},
  {time:5.038324,key:"SN:L",measure:1},
  {time:5.146237,key:"BD+RC:*",measure:2},
  {time:5.362065,key:"HH:R",measure:2},
  {time:5.577892,key:"SN:L",measure:2},
  {time:5.793719,key:"HH:R",measure:2},
  {time:6.009547,key:"BD:RF",measure:2},
  {time:6.225374,key:"HH:R",measure:2},
  {time:6.441201,key:"SN:L",measure:2},
  {time:6.657029,key:"HH:R",measure:2},
  {time:6.872856,key:"BD:RF",measure:3},
  {time:7.088683,key:"HH:R",measure:3},
  {time:7.304511,key:"SN:L",measure:3},
  {time:7.520338,key:"HH:R",measure:3},
  {time:7.736165,key:"BD:RF",measure:3},
  {time:7.951993,key:"HH:R",measure:3},
  {time:8.167820,key:"SN:L",measure:3},
  {time:8.383647,key:"HH:R",measure:3},
  {time:8.599475,key:"BD:RF",measure:4},
  {time:8.815302,key:"HH:R",measure:4},
  {time:9.031129,key:"SN:L",measure:4},
  {time:9.246957,key:"HH:R",measure:4},
  {time:9.462784,key:"BD:RF",measure:4},
  {time:9.678612,key:"HH:R",measure:4},
  {time:9.894439,key:"SN:L",measure:4},
  {time:10.110266,key:"HH:R",measure:4}
];
const viewports = [
  {name:"pc", width:1280, height:900},
  {name:"xperia-portrait", width:384, height:864}
];
const phases = [
  {name:"pre", offset:-0.015},
  {name:"hit", offset:0.030},
  {name:"rebound", offset:0.190},
  {name:"post", offset:0.300}
];
const browser = await chromium.launch({headless:true});
const root = "qa-artifacts";
await fs.mkdir(root,{recursive:true});
const summary = {url:URL, generatedAt:new Date().toISOString(), records:[]};

for (const vp of viewports) {
  const context = await browser.newContext({viewport:{width:vp.width,height:vp.height}, deviceScaleFactor:1});
  const page = await context.newPage();
  const errors=[];
  page.on("console",m=>{ if(m.type()==="error") errors.push("console: "+m.text()); });
  page.on("pageerror",e=>errors.push("pageerror: "+String(e)));
  await page.goto(URL,{waitUntil:"networkidle",timeout:120000});
  await page.waitForFunction(()=>window.__DTX_APP_READY__===true,{timeout:30000});
  await page.waitForFunction(()=>{
    const el=document.getElementById("characterBackdrop");
    return el && el.classList.contains("character-ready") && el.dataset.state;
  },{timeout:30000});

  const dir=path.join(root,vp.name);
  await fs.mkdir(dir,{recursive:true});
  for (let i=0;i<events.length;i++) {
    const ev=events[i];
    for (const ph of phases) {
      const t=Math.max(0,ev.time+ph.offset);
      await page.evaluate((time)=>{
        const timeline=document.getElementById("timeline");
        timeline.value=String(time);
        timeline.dispatchEvent(new Event("input",{bubbles:true}));
      },t);
      await page.waitForTimeout(100);
      const dom=await page.evaluate(()=>{
        const root=document.getElementById("characterBackdrop");
        const char=document.getElementById("characterLayer");
        const drum=document.getElementById("drumLayer");
        const stage=document.querySelector(".stage");
        const canvas=document.getElementById("laneCanvas");
        const rr=root.getBoundingClientRect(), cr=char.getBoundingClientRect(), dr=drum.getBoundingClientRect(), sr=stage.getBoundingClientRect(), lr=canvas.getBoundingClientRect();
        return {
          currentTime:document.getElementById("currentTime")?.textContent,
          frame:root.dataset.frame||"",
          phase:root.dataset.phase||"",
          animationKey:root.dataset.animationKey||"",
          limbs:root.dataset.limbs||"",
          state:root.dataset.state||"",
          active:root.dataset.active||"",
          assetIssue:root.dataset.assetIssue||"",
          initError:root.dataset.initError||"",
          pose:root.dataset.pose||"",
          sizes:{
            root:{x:rr.x,y:rr.y,w:rr.width,h:rr.height},
            character:{x:cr.x,y:cr.y,w:cr.width,h:cr.height,naturalWidth:char.naturalWidth,naturalHeight:char.naturalHeight},
            drum:{x:dr.x,y:dr.y,w:dr.width,h:dr.height,naturalWidth:drum.naturalWidth,naturalHeight:drum.naturalHeight},
            stage:{x:sr.x,y:sr.y,w:sr.width,h:sr.height},
            canvas:{x:lr.x,y:lr.y,w:lr.width,h:lr.height}
          }
        };
      });
      const safeKey=ev.key.replace(/[^A-Za-z0-9]+/g,"_");
      const base=`${String(i+1).padStart(2,"0")}_m${ev.measure}_${ev.time.toFixed(6)}_${safeKey}_${ph.name}`;
      await page.locator(".stage").screenshot({path:path.join(dir,base+".png")});
      summary.records.push({viewport:vp.name,event:ev,sample:ph.name,sampleTime:t,dom,screenshot:path.join(vp.name,base+".png")});
    }
  }
  summary[vp.name]={errors};
  await context.close();
}
await fs.writeFile(path.join(root,"runtime-qa.json"),JSON.stringify(summary,null,2));
await browser.close();
