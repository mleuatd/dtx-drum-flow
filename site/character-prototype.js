// DTX Drum Flow — instrument-only cyan watercolor glow (30 reference patterns).
// All coordinates are in the original drum image's 1400x1050 equivalent viewBox.
// No human/performer assets are fetched or rendered.
const NS="http://www.w3.org/2000/svg";
const DRUM="./character-assets/layers/drum/drum_base.png";
const PART_SHAPES={
  LC:["M208 122 Q252 64 352 100 Q465 126 571 232 Q563 265 506 253 Q340 232 208 157 Z"],
  HH:["M118 411 Q145 383 264 385 Q357 384 390 421 Q374 463 260 465 Q155 467 124 443 Z","M249 263 L279 263 L282 805 L248 809 Z","M240 816 L276 807 L373 973 L306 989 Z"],
  LP:["M240 817 L275 807 L377 974 L311 989 Z"],
  SN:["M346 515 Q463 460 604 502 L612 624 Q498 672 352 620 Z"],
  BD:["M528 573 Q576 519 718 520 Q867 547 921 714 Q927 858 803 925 Q644 966 546 866 Q507 748 528 573 Z","M686 712 L731 708 L745 911 L684 913 Z","M667 901 L744 892 L742 1006 L596 1010 Z"],
  HT:["M447 314 Q550 297 682 362 L660 501 Q542 521 428 477 Z"],
  LT:["M706 376 Q834 348 952 401 L965 549 Q840 581 700 526 Z"],
  FT:["M951 490 Q1110 439 1268 510 L1294 821 Q1161 883 942 798 Z"],
  RD:["M597 270 Q652 209 791 206 Q914 200 963 255 Q947 304 809 327 Q675 342 606 304 Z"],
  RC:["M944 143 Q1010 76 1161 80 Q1304 63 1318 128 Q1260 208 1095 250 Q966 253 942 188 Z"],
  LB:["M668 716 L724 715 L746 916 L681 912 Z","M650 894 L734 886 L740 1016 L593 1011 Z"]
};
// 30 distinct named preview/test patterns: 11 single instruments and 19 common simultaneous hits.
// Actual playback supports ANY combination of parts, not only these 30.
export const GLOW_PATTERNS=[
 ["LC"],["HH"],["LP"],["SN"],["BD"],["HT"],["LT"],["FT"],["RD"],["RC"],["LB"],
 ["HH","SN"],["HH","BD"],["HH","SN","BD"],["RD","SN"],["RD","BD"],["RC","BD"],
 ["LC","BD"],["SN","BD"],["HT","BD"],["LT","BD"],["FT","BD"],
 ["HH","LP"],["HH","RC"],["RD","SN","BD"],["RC","SN","BD"],
 ["LC","SN","BD"],["HT","LT"],["LT","FT"],["HH","SN","BD","RC"]
];
const state={root:null,svg:null,layer:null,notes:[],active:new Set(),ready:false,preview:-1};
const node=(tag,attrs={},parent)=>{const el=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));parent?.append(el);return el};
const emit=(ratio,failed=false)=>window.dispatchEvent(new CustomEvent("dtx-preload-progress",{detail:{kind:"character",ratio,label:"ドラム画像",failed:failed?1:0}}));
export function setDrumGlowNotes(notes){
 state.notes=(Array.isArray(notes)?notes:[]).filter(n=>Number.isFinite(Number(n.time))).map(n=>({time:Number(n.time),part:String(n.part||"").toUpperCase()})).sort((a,b)=>a.time-b.time);
}
const same=(a,b)=>a.size===b.size&&[...a].every(p=>b.has(p));
function render(parts,energy=0){
 if(!state.layer)return;
 if(same(parts,state.active)&&Math.abs((state.energy||0)-energy)<.035)return;
 state.active=new Set(parts);state.energy=energy;
 for(const group of state.layer.children){
   const on=parts.has(group.dataset.part);
   group.style.opacity=on?String(Math.max(.12,Math.min(1,energy))):"0";
 }
 state.root.dataset.glowParts=[...parts].join("+");
}
function makeGlow(){
 const root=state.root;
 root.querySelectorAll("#characterLayer,#drumFrontLayer,#characterFrontLayer,#hairFrontLayer,#effectLayer,#characterPoseLabel").forEach(x=>x.remove());
 const img=root.querySelector("#drumLayer");
 img.src=DRUM+"?v=20261106-drum-glow";
 img.alt="ドラムセット";
 img.onload=()=>{root.classList.add("active","drum-glow-ready");state.ready=true;emit(1)};
 img.onerror=()=>{root.dataset.initError="drum_image_load_failed";emit(1,true)};
 if(img.complete&&img.naturalWidth){root.classList.add("active","drum-glow-ready");state.ready=true;emit(1)}
 const svg=node("svg",{viewBox:"0 0 1400 1050",preserveAspectRatio:"xMidYMid meet","aria-hidden":"true",class:"drum-glow-svg"},root);
 const defs=node("defs",{},svg);
 const filter=node("filter",{id:"dtx-watercolor-blur",x:"-40%",y:"-40%",width:"180%",height:"180%"},defs);
 node("feGaussianBlur",{stdDeviation:"14"},filter);
 const ink=node("filter",{id:"dtx-watercolor-soft",x:"-30%",y:"-30%",width:"160%",height:"160%"},defs);
 node("feGaussianBlur",{stdDeviation:"3.5"},ink);
 const layer=node("g",{class:"drum-glow-groups"},svg);
 for(const [part,paths] of Object.entries(PART_SHAPES)){
   const g=node("g",{"data-part":part,class:"drum-glow-part"},layer);
   g.dataset.part=part;g.style.opacity="0";
   for(const d of paths){
     node("path",{d,fill:"#008cff","fill-opacity":".78",stroke:"#008dff","stroke-width":"17","stroke-opacity":".65",filter:"url(#dtx-watercolor-blur)"},g);
     node("path",{d,fill:"#21a6ff","fill-opacity":".41",stroke:"#006fff","stroke-width":"4","stroke-opacity":".56",filter:"url(#dtx-watercolor-soft)"},g);
     node("path",{d,fill:"#30baff","fill-opacity":".13",stroke:"#71d7ff","stroke-width":"2","stroke-opacity":".40"},g);
   }
 }
 state.svg=svg;state.layer=layer;
}
export async function initCharacterPrototype(){
 state.root=document.getElementById("characterBackdrop");
 if(!state.root){emit(1,true);return}
 emit(0);
 makeGlow();
 const q=new URLSearchParams(location.search);
 if(q.has("glowPreview")){
   const i=Number(q.get("glowPreview"));state.preview=Number.isFinite(i)?Math.max(0,Math.min(29,Math.trunc(i))):0;
 }
 window.__DTX_DRUM_GLOW__={patterns:GLOW_PATTERNS,showPattern(i){state.preview=Math.max(0,Math.min(29,Number(i)||0));render(new Set(GLOW_PATTERNS[state.preview]),1)},resume(){state.preview=-1},get state(){return {ready:state.ready,parts:[...state.active],count:state.notes.length}}};
}
export function updateCharacterPrototype(time,chartName="",playbackRate=1,isPlaying=false){
 if(!state.ready)return;
 if(state.preview>=0){render(new Set(GLOW_PATTERNS[state.preview]),1);return}
 if(!isPlaying||!state.notes.length){render(new Set(),0);return}
 const t=Number(time)||0,rate=Math.max(.25,Number(playbackRate)||1);
 // Glow begins before the scheduled strike; watercolor fades after the hit.
 const lead=.115*rate,trail=.18*rate;
 const parts=new Set();let energy=0;
 // Binary search to keep 2000+ note charts smooth on mobile devices.
 let lo=0,hi=state.notes.length;
 while(lo<hi){const mid=(lo+hi)>>1;if(state.notes[mid].time<t-trail)lo=mid+1;else hi=mid}
 for(let i=lo;i<state.notes.length;i++){
   const n=state.notes[i],delta=n.time-t;if(delta>lead)break;
   const intensity=delta>=0?(.4+.6*(1-delta/lead)):(1+delta/trail)*.95;
   if(intensity>.04){parts.add(n.part);energy=Math.max(energy,intensity)}
 }
 render(parts,energy);
}
