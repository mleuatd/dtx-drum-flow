import fs from "node:fs";
const SR=48000,DUR=3.2,N=Math.floor(SR*DUR),voices=["kick","snare","hihatClosed","tomHigh","ride","crashLeft"];
const seq=[
 ["crashLeft",0],["kick",.06],["snare",.12],["hihatClosed",.18],["kick",.24],["tomHigh",.30],["kick",.36],["ride",.42],
 ["kick",.48],["snare",.54],["hihatClosed",.60],["kick",.66],["crashLeft",.72],["kick",.78],["snare",.84],["kick",.90],
 ["ride",1.0],["kick",1.03],["kick",1.09],["snare",1.15],["kick",1.21],["tomHigh",1.27],["kick",1.33],["crashLeft",1.39]
];
const x=new Float64Array(N);
function addKick(t,a=0.75){let s=Math.floor(t*SR);for(let i=0;i<.42*SR&&s+i<N;i++){let q=i/SR,e=Math.exp(-q*12),f=52+(115-52)*Math.exp(-q*18);x[s+i]+=a*Math.sin(2*Math.PI*f*q)*e}}
function addNoise(t,a=.18,d=.18){let s=Math.floor(t*SR),z=1;for(let i=0;i<d*SR&&s+i<N;i++){z=(z*1664525+1013904223)>>>0;let n=(z/4294967296)*2-1;x[s+i]+=a*n*Math.exp(-(i/SR)*18)}}
function addTone(t,a=.16,f=180,d=.25){let s=Math.floor(t*SR);for(let i=0;i<d*SR&&s+i<N;i++){let q=i/SR;x[s+i]+=a*Math.sin(2*Math.PI*f*q)*Math.exp(-q*13)}}
function addCym(t,a=.07,d=1.5){let s=Math.floor(t*SR),z=7;for(let i=0;i<d*SR&&s+i<N;i++){z=(z*1103515245+12345)>>>0;let n=(z/4294967296)*2-1;x[s+i]+=a*n*Math.exp(-(i/SR)*2.5)}}
for(const [v,t] of seq){if(v==="kick")addKick(t);else if(v==="snare")addNoise(t);else if(v==="tomHigh")addTone(t);else if(v==="hihatClosed")addCym(t,.045,.12);else addCym(t)}
let rawPeak=0;for(let i=0;i<N;i++)rawPeak=Math.max(rawPeak,Math.abs(x[i]));const safety=rawPeak>.92?.92/rawPeak:1;for(let i=0;i<N;i++)x[i]*=safety;let peak=0,clip=0,maxJump=0,jumpAt=0;for(let i=0;i<N;i++){peak=Math.max(peak,Math.abs(x[i]));if(Math.abs(x[i])>=.999)clip++;if(i){let j=Math.abs(x[i]-x[i-1]);if(j>maxJump){maxJump=j;jumpAt=i/SR}}}
const onsetWindows=seq.map(([voice,t])=>{let s=Math.floor(t*SR),pre=0,post=0;for(let i=Math.max(1,s-240);i<s;i++)pre=Math.max(pre,Math.abs(x[i]-x[i-1]));for(let i=s;i<Math.min(N,s+240);i++)post=Math.max(post,Math.abs(x[i]-x[i-1]));return{voice,time:t,preJump:pre,postJump:post,discontinuity:Math.max(0,post-pre)}})
const report={sampleRate:SR,duration:DUR,events:seq.length,rawPeak,safetyGain:safety,peak,clippedSamples:clip,maxAdjacentJump:maxJump,maxJumpAtSec:jumpAt,onsetWindows,status:clip===0&&maxJump<1.25?"PASS":"REVIEW"};
fs.mkdirSync("qa/audio-smoothness",{recursive:true});fs.writeFileSync("qa/audio-smoothness/report.json",JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(report.status!=="PASS")process.exit(1);
