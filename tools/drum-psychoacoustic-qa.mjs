import fs from "node:fs";
const engine=fs.readFileSync("site/live-drum-engine.js","utf8");
const app=fs.readFileSync("site/app.js","utf8");
const rules=[];
const add=(id,ok,detail)=>rules.push({id,ok,detail});
add("no-synthetic-kick",!engine.includes("_kickBody(")&&!engine.includes('o.type="sine"'),"BD must remain acoustic-sample based");
add("sample-tail-overlap",!/(kick|snare|tomHigh|tomLow|tomFloor)[^\n]{0,120}\.stop\(/.test(engine),"short drums must not be hard-cut by a later hit");
const attacks=[...engine.matchAll(/comp\.attack\.value=([.\d]+)/g),...app.matchAll(/comp\.attack\.value=([.\d]+)/g)].map(m=>+m[1]);
const releases=[...engine.matchAll(/comp\.release\.value=([.\d]+)/g),...app.matchAll(/comp\.release\.value=([.\d]+)/g)].map(m=>+m[1]);
const ratios=[...engine.matchAll(/comp\.ratio\.value=([.\d]+)/g),...app.matchAll(/comp\.ratio\.value=([.\d]+)/g)].map(m=>+m[1]);
add("compressor-attack",attacks.every(v=>v>=.005),attacks);
add("compressor-release",releases.every(v=>v>=.04&&v<=.25),releases);
add("compressor-ratio",ratios.every(v=>v<=2),ratios);
add("micro-fade-in",/linearRampToValueAtTime\(strength,when\+\.002\)/.test(engine),"2ms attack ramp expected");
add("cymbal-tail-not-abrupt",/exponentialRampToValueAtTime\(\.0008,fadeEnd\)/.test(engine),"cymbal tails use exponential fade");
const scenarios=[
 {id:"crash-kick-mask",spacingMs:[0,45,90,180,360],purpose:"cymbal tail + kick masking/pumping"},
 {id:"ride-16th-kick",spacingMs:[0,60,120,180,240,300],purpose:"ride sustain + dense kick"},
 {id:"crash-snare-kick",spacingMs:[0,25,50,75,100,125],purpose:"dense transient stacking"},
 {id:"tom-fill-crash",spacingMs:[0,80,160,240,320],purpose:"tail continuity through fill"},
 {id:"double-kick",spacingMs:[0,45,90,135,180],purpose:"rapid BD overlap"}
];
const report={baseline:"r20",goal:"conservative psychoacoustic regression gate; flags common click, pumping, tail-cut and overlap risks",rules,scenarios,status:rules.every(r=>r.ok)?"PASS":"REVIEW"};
fs.mkdirSync("qa/audio-smoothness",{recursive:true});fs.writeFileSync("qa/audio-smoothness/psychoacoustic-report.json",JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(report.status!=="PASS")process.exit(1);
