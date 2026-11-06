// Lightweight, offline drum-onset estimation for a user-supplied audio file.
// This is intentionally an APPROXIMATE transcription, not a licensed/exact score.
// No external service or network request is used.
export function estimateDrumChart(audioBuffer,{bpm=183,name="音源から推定したドラム譜面"}={}){
 const sampleRate=audioBuffer.sampleRate;
 const channels=audioBuffer.numberOfChannels;
 const channelData=Array.from({length:channels},(_,i)=>audioBuffer.getChannelData(i));
 const stride=Math.max(1,Math.round(sampleRate/11025));
 const reducedRate=sampleRate/stride;
 const hop=Math.max(32,Math.round(reducedRate*.010));
 const bands=3,n=Math.ceil(audioBuffer.length/(stride*hop));
 const values=Array.from({length:bands},()=>new Float32Array(n));
 let low=0,trebleLow=0,row=0,totals=[0,0,0],count=0;
 const alphaLow=1-Math.exp(-2*Math.PI*175/reducedRate);
 const alphaHigh=1-Math.exp(-2*Math.PI*2700/reducedRate);
 for(let p=0;p<audioBuffer.length;p+=stride){
   let sample=0;
   for(let k=0;k<channels;k++)sample+=channelData[k][p]/channels;
   low+=alphaLow*(sample-low);
   trebleLow+=alphaHigh*(sample-trebleLow);
   const mid=trebleLow-low,high=sample-trebleLow;
   totals[0]+=low*low;totals[1]+=mid*mid;totals[2]+=high*high;
   count++;
   if(count===hop){
     for(let j=0;j<bands;j++){values[j][row]=Math.sqrt(totals[j]/count);totals[j]=0}
     row++;count=0;
   }
 }
 if(count&&row<n)for(let j=0;j<bands;j++)values[j][row]=Math.sqrt(totals[j]/count);
 const novelty=values.map(v=>{
   const z=new Float32Array(n);
   for(let i=2;i<n;i++)z[i]=Math.max(0,v[i]-v[i-2]);
   return z;
 });
 const thresholds=novelty.map(z=>{
   const s=Float32Array.from(z).sort();
   return {p85:s[Math.floor(s.length*.85)]||0,p95:s[Math.floor(s.length*.95)]||0,p99:s[Math.floor(s.length*.99)]||0};
 });
 const notes=[];
 const last=[-1,-1,-1];
 const minDist=[.100,.105,.075];
 const tags=[{part:"BD",kind:"kick",gmNote:36},{part:"SN",kind:"snare",gmNote:38},{part:"HH",kind:"hihat",gmNote:42}];
 for(let i=3;i<n-2;i++){
   const t=(i*hop+hop/2)/reducedRate;
   for(let band=0;band<bands;band++){
     const z=novelty[band],value=z[i],limit=thresholds[band];
     if(!value||value<limit.p85*.73||value<limit.p95*.26)continue;
     if(value<z[i-1]||value<z[i+1])continue;
     if(t-last[band]<minDist[band])continue;
     // Reject continuous melodic/bass energy and aim at abrupt transient bursts.
     const base=values[band];
     const previous=Math.max(base[i-3],base[i-4],base[i-5]);
     if(base[i]<previous*1.13&&value<limit.p99*.6)continue;
     const relative=limit.p95?value/limit.p95:0;
     // More conservative high-frequency onset gating: full mixes contain vocals.
     if(band===2&&relative<.63)continue;
     last[band]=t;
     const tag=tags[band],confidence=Math.min(.68,Math.max(.24,relative*.35));
     notes.push({
       time:Number(Math.max(0,t-.01).toFixed(6)),part:tag.part,kind:tag.kind,
       gmNote:tag.gmNote,velocity:Math.min(.95,.5+Math.min(1,relative)*.4),
       confidence:Number(confidence.toFixed(3)),estimated:true
     });
   }
 }
 notes.sort((a,b)=>a.time-b.time);
 return {
   name,artist:"初星学園",bpm,
   duration:audioBuffer.duration,notes,
   source:"音源からの自動推定（精度未検証・端末内処理）",
   estimated:true,
   alignment:{method:"ユーザーが選んだ音源のトランジェントを推定",pendingOriginalAudioSync:false},
   estimationNotice:"ドラム原譜ではありません。音源の低・中・高域の立ち上がりから推定した暫定ノーツです。"
 };
}
