// Sample-based acoustic drum engine for DTX Drum Flow.
// Uses CC0 Virtuosity Drums-derived FLAC files maintained by the ferrosintesis project.
// Luna say maybe is a timbral/reference target only; no source recording is redistributed.

const CORE="https://raw.githubusercontent.com/0x4D44/ferrosintesis/main/crates/ferrosintesis-samples-drumkit/samples/";
const CYM="https://raw.githubusercontent.com/0x4D44/ferrosintesis/main/crates/ferrosintesis-samples-drumkit2/samples/";
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const defs={
 kick:{base:CORE,prefix:"kick",layers:4,rr:4},snare:{base:CORE,prefix:"snare",layers:6,rr:3},
 sideStick:{base:CORE,prefix:"sidestick",layers:3,rr:3},hihatClosed:{base:CORE,prefix:"hhc",layers:4,rr:4},
 hihatOpen:{base:CORE,prefix:"hho",layers:4,rr:3},hihatPedal:{base:CORE,prefix:"hhp",layers:3,rr:4},
 tomHigh:{base:CORE,prefix:"tomhi",layers:4,rr:3},tomLow:{base:CORE,prefix:"tomlo",layers:4,rr:3},
 tomFloor:{base:CORE,prefix:"tomlo",layers:4,rr:3},ride:{base:CORE,prefix:"ride",layers:3,rr:4},
 rideBell:{base:CORE,prefix:"ridebell",layers:3,rr:3},crashLeft:{base:CYM,prefix:"crash",layers:3,rr:4},
 crashRight:{base:CYM,prefix:"crash",layers:3,rr:4}
};
function voiceFor(part,note={}){
 const k=note.soundKey||note.drumVoice;
 if(k&&defs[k])return k;
 const gm=Number(note.gmNote),a=String(note.articulation||"").toLowerCase();
 if(gm===37)return"sideStick";if(gm===44||a==="pedal")return"hihatPedal";if(gm===46||a==="open")return"hihatOpen";
 if(gm===53||a==="bell")return"rideBell";if(part==="BD"||part==="LB")return"kick";if(part==="SN")return"snare";
 if(part==="HH")return"hihatClosed";if(part==="LP")return"hihatPedal";if(part==="HT")return"tomHigh";
 if(part==="LT")return"tomLow";if(part==="FT")return"tomFloor";if(part==="RD")return"ride";
 if(part==="LC")return"crashLeft";if(part==="RC")return"crashRight";return"snare";
}
export class LiveDrumEngine{
 constructor(ctx,destination){this.ctx=ctx;this.destination=destination;this.buffers=new Map();this.loading=new Map();this.rr=new Map();this.nodes=new Set();this.ready=false;this._buildBus()}
 _buildBus(){const c=this.ctx;this.input=c.createGain();this.comp=c.createDynamicsCompressor();this.out=c.createGain();this.input.gain.value=.95;this.comp.threshold.value=-13;this.comp.knee.value=9;this.comp.ratio.value=2.3;this.comp.attack.value=.004;this.comp.release.value=.16;this.out.gain.value=.96;this.input.connect(this.comp);this.comp.connect(this.out);this.out.connect(this.destination)}
 _url(v,l,r){const d=defs[v];return d.base+d.prefix+"_vl"+l+"_rr"+r+".flac"}
 async _load(v,l,r){const key=v+":"+l+":"+r;if(this.buffers.has(key))return this.buffers.get(key);if(this.loading.has(key))return this.loading.get(key);const p=fetch(this._url(v,l,r)).then(x=>{if(!x.ok)throw Error("sample "+x.status);return x.arrayBuffer()}).then(b=>this.ctx.decodeAudioData(b)).then(b=>(this.buffers.set(key,b),b)).catch(e=>(console.warn("drum sample fallback",key,e),null));this.loading.set(key,p);const b=await p;this.loading.delete(key);return b}
 async preload(){
  // Decoding 100+ FLAC files at once can starve the WebAudio render thread on phones
  // and present as clicks/pops. Keep network/decode pressure deliberately bounded.
  const jobs=[];for(const [v,d] of Object.entries(defs))for(let l=1;l<=d.layers;l++)for(let r=1;r<=d.rr;r++)jobs.push([v,l,r]);
  const workers=Array.from({length:3},async()=>{while(jobs.length){const [v,l,r]=jobs.shift();await this._load(v,l,r)}});
  await Promise.allSettled(workers);this.ready=true;return this
}
 _layer(v,velocity){const d=defs[v];return clamp(Math.ceil(clamp(velocity,0,1)*d.layers),1,d.layers)}
 _nextRR(v){const d=defs[v],n=((this.rr.get(v)||0)%d.rr)+1;this.rr.set(v,n);return n}
 trigger(part,velocity=.8,when=this.ctx.currentTime+.002,note={}){const v=voiceFor(part,note),layer=this._layer(v,velocity),rr=this._nextRR(v),key=v+":"+layer+":"+rr,buffer=this.buffers.get(key);if(buffer)return this._play(v,buffer,velocity,when);this._load(v,layer,rr).then(b=>{if(b&&when>=this.ctx.currentTime-.03)this._play(v,b,velocity,Math.max(when,this.ctx.currentTime+.002))});return null}
 _play(v,buffer,velocity,when){
  const c=this.ctx,s=c.createBufferSource(),g=c.createGain(),pan=c.createStereoPanner?c.createStereoPanner():null;
  const isCrash=v==="crashLeft"||v==="crashRight",isRide=v==="ride"||v==="rideBell";
  // Narrow dynamics for practice: retain accents, but prevent one family from dominating.
  const nv=clamp(velocity,0,1);
  const base=.70+.25*nv;
  // Near-equal perceived practice mix. Keep only small instrument-family differences.
  const familyGain=isCrash?.78:isRide?.84:(v==="hihatClosed"||v==="hihatOpen"||v==="hihatPedal")?.88:(v==="kick")?.97:(v==="snare")?.96:(v==="tomHigh"||v==="tomLow"||v==="tomFloor")?.98:1;
  const strength=base*familyGain;
  g.gain.setValueAtTime(strength,when);
  // Preserve audible cymbal presence, while shortening only the masking tail.
  if(isCrash){const fadeStart=when+.58,fadeEnd=when+1.42;g.gain.setValueAtTime(strength,fadeStart);g.gain.exponentialRampToValueAtTime(.0008,fadeEnd)}
  else if(isRide){const fadeStart=when+.68,fadeEnd=when+1.62;g.gain.setValueAtTime(strength,fadeStart);g.gain.exponentialRampToValueAtTime(.0008,fadeEnd)}
  s.buffer=buffer;s.playbackRate.value=1+(Math.random()-.5)*.006;
  if(pan){const p=v==="crashLeft"?-.28:v==="crashRight"?.28:v==="tomHigh"?-.12:v==="tomFloor"?.12:0;pan.pan.value=p;s.connect(g);g.connect(pan);pan.connect(this.input)}else{s.connect(g);g.connect(this.input)}
  s.start(when);if(isCrash)s.stop(Math.min(when+1.47,when+buffer.duration));else if(isRide)s.stop(Math.min(when+1.67,when+buffer.duration));
  this.nodes.add(s);s.addEventListener("ended",()=>this.nodes.delete(s),{once:true});return s
}
 stop(){for(const n of this.nodes){try{n.stop()}catch{}}this.nodes.clear()}
}
export {voiceFor as resolveLiveDrumVoice};
