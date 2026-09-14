const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));

export async function decodeAudio(file){
  const ctx=new (window.AudioContext||window.webkitAudioContext)();
  const buf=await ctx.decodeAudioData(await file.arrayBuffer());
  await ctx.close();
  return buf;
}

function mono(buffer){
  const out=new Float32Array(buffer.length);
  for(let ch=0;ch<buffer.numberOfChannels;ch++){const d=buffer.getChannelData(ch);for(let i=0;i<out.length;i++)out[i]+=d[i]/buffer.numberOfChannels}
  return out;
}

function rmsEnvelope(data,sr,windowMs=12,hopMs=4){
  const win=Math.max(32,Math.round(sr*windowMs/1000)),hop=Math.max(8,Math.round(sr*hopMs/1000));
  const env=[];for(let s=0;s+win<data.length;s+=hop){let e=0;for(let i=s;i<s+win;i++)e+=data[i]*data[i];env.push(Math.sqrt(e/win))}
  return {env:Float32Array.from(env),hop};
}

function spectralLikeFlux(env){
  const flux=new Float32Array(env.length);for(let i=1;i<env.length;i++)flux[i]=Math.max(0,env[i]-env[i-1]);return flux;
}

function localPeaks(flux,minDistance){
  const vals=Array.from(flux).sort((a,b)=>a-b),median=vals[Math.floor(vals.length*.5)]||0,p90=vals[Math.floor(vals.length*.9)]||median;
  const threshold=median+(p90-median)*.35,peaks=[];let last=-1e9;
  for(let i=1;i<flux.length-1;i++)if(flux[i]>=threshold&&flux[i]>=flux[i-1]&&flux[i]>=flux[i+1]&&i-last>=minDistance){peaks.push({i,strength:flux[i]});last=i}
  return peaks;
}

function beatGridScore(t,bpm,offset=0){
  if(!bpm)return 0;const beat=60/bpm,phase=((t-offset)%beat+beat)%beat,d=Math.min(phase,beat-phase);return 1-clamp(d/(beat*.22),0,1);
}

export function analyzeOnsets(buffer,bpm){
  const d=mono(buffer),{env,hop}=rmsEnvelope(d,buffer.sampleRate),flux=spectralLikeFlux(env);
  const minDistance=Math.max(1,Math.round(.035*buffer.sampleRate/hop));
  return localPeaks(flux,minDistance).map(p=>({time:p.i*hop/buffer.sampleRate,strength:p.strength,beatScore:beatGridScore(p.i*hop/buffer.sampleRate,bpm)}));
}

export function realignNotes(notes,onsets,bpm,{windowMs=140,maxShiftMs=110}={}){
  if(!onsets.length)return {notes,stats:{moved:0,meanShiftMs:0}};
  const window=windowMs/1000,maxShift=maxShiftMs/1000;let moved=0,total=0;
  const aligned=[];
  for(let idx=0;idx<notes.length;idx++){
    const n=notes[idx];
    let best=null,bestScore=-Infinity;
    for(const o of onsets){const dt=o.time-n.time;if(dt<-window)continue;if(dt>window)break;
      const proximity=1-Math.min(1,Math.abs(dt)/window);
      const prevTime=idx>0?(aligned[idx-1]?.time??notes[idx-1].time):null;
      const pattern=idx>0?Math.max(0,1-Math.abs((o.time-prevTime)-(n.time-notes[idx-1].time))/.12):.5;
      const score=proximity*.58+o.beatScore*.22+Math.min(1,o.strength*25)*.15+pattern*.05;
      if(score>bestScore){bestScore=score;best=o}
    }
    if(!best||bestScore<.38){aligned.push({...n,alignConfidence:0});continue}
    const shift=clamp(best.time-n.time,-maxShift,maxShift),time=n.time+shift;
    if(Math.abs(shift)>.004){moved++;total+=Math.abs(shift)}
    aligned.push({...n,time,alignConfidence:clamp(bestScore,0,1),originalTime:n.time});
  }
  aligned.sort((a,b)=>a.time-b.time);
  return {notes:aligned,stats:{moved,meanShiftMs:moved?total/moved*1000:0}};
}
