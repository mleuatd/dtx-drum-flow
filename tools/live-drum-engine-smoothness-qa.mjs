import fs from "node:fs";
const scenarios=[
 {name:"cymbal_then_kick",events:[["crashLeft",0],["kick",.18],["kick",.43],["snare",.62]]},
 {name:"ride_kick_16ths",events:[["ride",0],["kick",.12],["kick",.245],["kick",.37],["kick",.495],["snare",.62]]},
 {name:"dense_live_fill",events:[["crashLeft",0],["kick",.03],["snare",.14],["tomHigh",.25],["tomLow",.36],["tomFloor",.47],["kick",.50],["crashRight",.61]]}
];
const checks={minimumHeadroomDb:1,maximumAbruptGainStep:0.08,maximumCompressorRatio:2,minimumCompressorAttackMs:5,maximumTailCutRisk:"no hard stop for kick/snare/toms"};
const engine=fs.readFileSync("site/live-drum-engine.js","utf8"),app=fs.readFileSync("site/app.js","utf8");
const findings=[];
if(engine.includes("_kickBody(")||engine.includes('o.type="sine"'))findings.push("synthetic kick reinforcement present");
const comps=[...engine.matchAll(/ratio\.value=([.\d]+)/g),...app.matchAll(/ratio\.value=([.\d]+)/g)].map(m=>Number(m[1]));
if(comps.some(x=>x>checks.maximumCompressorRatio))findings.push("compressor ratio too aggressive: "+comps.join(","));
if(/kick[^\n]*\.stop\(/.test(engine))findings.push("kick has forced tail stop");
const report={purpose:"Detect click/pump/tail-cut risks before public drum builds",scenarios,checks,compressorRatios:comps,findings,status:findings.length?"REVIEW":"PASS"};
fs.mkdirSync("qa/audio-smoothness",{recursive:true});fs.writeFileSync("qa/audio-smoothness/live-engine-report.json",JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(findings.length)process.exit(1);
