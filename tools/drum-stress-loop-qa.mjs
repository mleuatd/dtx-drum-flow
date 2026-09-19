import fs from "node:fs";
const rounds=8,results=[];
for(let r=1;r<=rounds;r++){
 const SR=48000,D=2.4,N=SR*D,x=new Float64Array(N);let seed=0x51f15e+r;
 const rnd=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296)*2-1;
 const addKick=t=>{const s=t*SR|0;for(let i=0;i<.38*SR&&s+i<N;i++){const q=i/SR;x[s+i]+=.48*Math.sin(2*Math.PI*(48+70*Math.exp(-q*20))*q)*Math.exp(-q*11)}};
 const addCym=t=>{const s=t*SR|0;for(let i=0;i<1.25*SR&&s+i<N;i++)x[s+i]+=.055*rnd()*Math.exp(-(i/SR)*2.7)};
 const addSn=t=>{const s=t*SR|0;for(let i=0;i<.2*SR&&s+i<N;i++)x[s+i]+=.13*rnd()*Math.exp(-(i/SR)*20)};
 addCym(0);for(let t=.04;t<1.4;t+=.06+(r%3)*.015)addKick(t);for(let t=.12;t<1.3;t+=.24)addSn(t);addCym(.72);
 let raw=0;for(const v of x)raw=Math.max(raw,Math.abs(v));const gain=raw>.9?.9/raw:1;let jump=0,clip=0,dc=0,sum=0;
 for(let i=0;i<N;i++){x[i]*=gain;sum+=x[i]*x[i];dc+=x[i];if(Math.abs(x[i])>=.999)clip++;if(i)jump=Math.max(jump,Math.abs(x[i]-x[i-1]))}
 const rms=Math.sqrt(sum/N),dcAbs=Math.abs(dc/N);results.push({round:r,rawPeak:raw,safetyGain:gain,peak:raw*gain,rms,maxAdjacentJump:jump,clippedSamples:clip,dcAbs,pass:clip===0&&jump<.65&&dcAbs<.01});
}
const report={rounds,results,status:results.every(x=>x.pass)?"PASS":"REVIEW"};fs.mkdirSync("qa/audio-smoothness",{recursive:true});fs.writeFileSync("qa/audio-smoothness/stress-loop-report.json",JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(report.status!=="PASS")process.exit(1);
