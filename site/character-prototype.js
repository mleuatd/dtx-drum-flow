const PROTOTYPE_URL="./charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json";
const DEFAULT_MEASURE_START=1;
const DEFAULT_MEASURE_END=4;
const LIMB_URL="./charts/luna_say_maybe/Luna_say_maybe_full_limbs.json";
const INVENTORY_URL="./character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json";
const ASSET_ROOT="./character-assets";
const ASSET_VERSION="20260919-public-runtime-qa-r1";
const DRUM="./character-assets/layers/drum/drum_base.png";
const assetUrl=src=>src+(src.includes("?")?"&":"?")+"v="+ASSET_VERSION;

let data=null,lastKey="",lastEffectToken="",ready=false,activeSong=false;
const els={root:null,drum:null,character:null,label:null,effect:null,bursts:[]};
function updateDevHud(extra=""){
  const hud=document.getElementById("devBuildHud");
  if(!hud)return;
  const root=document.getElementById("characterBackdrop");
  const lines=[
    "BUILD 20260918-inventory-scope-r1",
    "JS:ok / CHAR:"+(ready?"ready":"loading"),
    "active:"+(root?.dataset.active||"-")+" state:"+(root?.dataset.state||"-"),
    "frame:"+(root?.dataset.frame||"-"),
    "phase:"+(root?.dataset.phase||"-"),
    "key:"+(root?.dataset.animationKey||"-"),
    "err:"+(root?.dataset.initError||root?.dataset.assetIssue||"-")
  ];
  if(extra)lines.push(extra);
  hud.textContent=lines.join("\n");
}
setInterval(()=>updateDevHud(),250);
const EFFECT_POINTS={HH:[190,390],SN:[420,535],BD:[735,650],HT:[575,360],LT:[885,455],FT:[1165,535],RC:[1215,145],RD:[965,250]};

function loadImage(src){return new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(src);image.onerror=()=>reject(new Error("image HTTP/load failure: "+src));image.src=assetUrl(src)})}
function markAssetIssue(src){if(!els.root)return;els.root.dataset.assetIssue=src||"unknown";els.root.classList.add("asset-warning")}
function groupNotes(notes){const groups=[];for(const n of notes){const g=groups.at(-1);if(g&&Math.abs(n.time-g[0].time)<=.008)g.push(n);else groups.push([n])}return groups}
function noteIdentity(note){return [Number(note?.time).toFixed(6),note?.part||""].join("|")}
function handForNote(note){if(note?.limb)return note.limb;if(note?.animation?.limb)return note.animation.limb;if(note?.animation?.hand)return note.animation.hand;if(note?.animation?.foot)return note.animation.foot;if(note?.part==="SN")return "L";if(note?.part==="BD")return "RF";if(note?.part==="LP"||note?.part==="LB")return "LF";return "R"}
function fallbackInfo(group){if(!group?.length)return {fallback:false,reason:""};const key=keyFor(group);if(!data?.frameMap?.[key])return {fallback:true,reason:"missing-exact-frame"};if(data?.fallbackKeys?.has(key))return {fallback:true,reason:"declared-fallback-key"};return {fallback:false,reason:""}}
function exactKeyFor(group){const notes=[...group].sort((a,b)=>a.part.localeCompare(b.part));if(notes.length>1)return notes.map(n=>n.part).join("+")+":"+notes.map(n=>handForNote(n)).join("/");const n=notes[0];return n.part+":"+handForNote(n)}
function keyFor(group,frameMap=data?.frameMap){const exact=exactKeyFor(group);if(frameMap?.[exact])return exact;const parts=[...new Set(group.map(n=>n.part))].sort();if(parts.length>1){const combo=parts.join("+")+":*";if(frameMap?.[combo])return combo}return exact}
function assetFor(group,phase="hit"){if(phase==="neutral")return data?.frames?.neutral?.path||"layers/character/base/neutral.png";const key=keyFor(group);const phases=data?.phaseFrameMap?.[key];const frameId=phases?.[phase]||data?.frameMap?.[key]||"neutral";return data?.frames?.[frameId]?.path||"layers/character/base/neutral.png"}
function validatePrototypeCoverage(inventory,scopedNotes,groups){const scope=inventory.runtimeScope||{};if(scopedNotes.length!==Number(scope.noteCount||0))throw new Error("prototype note count mismatch");if(groups.length!==Number(scope.groupCount||0))throw new Error("prototype group count mismatch");if(scopedNotes.some(note=>!note.limb))throw new Error("prototype limb assignments missing");const expectedKeys=new Set(scope.expectedKeys||[]),actualKeys=new Set();for(const group of groups){const key=keyFor(group,inventory.runtimeFrameMap);actualKeys.add(key);if(!inventory.runtimeFrameMap?.[key])throw new Error("prototype frame missing for "+key);for(const phase of ["prep","hit","rebound"]){const frameId=inventory.runtimePhaseFrameMap?.[key]?.[phase];if(!frameId||!inventory.requiredFrames?.[frameId])throw new Error("prototype phase frame missing for "+key+"."+phase)}}const missing=[...expectedKeys].filter(key=>!actualKeys.has(key)),unexpected=[...actualKeys].filter(key=>!expectedKeys.has(key));if(missing.length||unexpected.length)throw new Error("prototype key mismatch missing="+missing.join(",")+" unexpected="+unexpected.join(","))}
function setFrame(path,label="",phase="neutral"){if(!els.character)return;const src=assetUrl(ASSET_ROOT+"/"+path);if(lastKey!==src){lastKey=src;els.character.src=src}if(els.label)els.label.textContent=label;if(els.root){els.root.dataset.frame=path;els.root.dataset.pose=label;els.root.dataset.phase=phase}}
function normalizedPlaybackRate(playbackRate=1){
  const rate=Number(playbackRate);
  return Number.isFinite(rate)&&rate>0?rate:1;
}
function findGroupAt(time,playbackRate=1){
  if(!data?.groups?.length)return null;
  let previous=null;
  for(const group of data.groups){
    if(group[0].time<=time)previous=group;
    else break;
  }
  if(!previous)return null;
  const rate=normalizedPlaybackRate(playbackRate);
  const deltaReal=(Number(time)-previous[0].time)/rate;
  const reboundEndReal=Number(data?.motionTiming?.reboundEndSeconds??.17);
  return deltaReal<=reboundEndReal?previous:null;
}
function phaseFor(group,time,playbackRate=1){
  const rate=normalizedPlaybackRate(playbackRate);
  const deltaReal=(Number(time)-group[0].time)/rate;
  const timing=data?.motionTiming||{};
  const baseHitEndReal=Number(timing.hitEndSeconds??.09);
  const baseReboundEndReal=Number(timing.reboundEndSeconds??.17);
  const index=data?.groups?.indexOf(group)??-1;
  const nextTime=index>=0?Number(data?.groups?.[index+1]?.[0]?.time):NaN;
  const gapReal=Number.isFinite(nextTime)?Math.max(0,(nextTime-Number(group[0].time))/rate):Infinity;
  let hitEndReal=baseHitEndReal,reboundEndReal=baseReboundEndReal;

  // Human motion timing is real-time based, not chart-time based.
  // Fast passages flow directly into the next hit; slow playback naturally
  // leaves enough wall-clock time to finish rebound and return to neutral.
  if(Number.isFinite(gapReal)&&gapReal<baseReboundEndReal){
    hitEndReal=Math.min(baseHitEndReal,Math.max(.055,gapReal*.65));
    reboundEndReal=Math.min(baseReboundEndReal,Math.max(hitEndReal+.02,gapReal-.004));
  }
  if(deltaReal<0)return "neutral";
  if(deltaReal<hitEndReal)return "hit";
  if(deltaReal<reboundEndReal)return "rebound";
  return "neutral";
}
function triggerEffect(group,phase){if(!els.effect)return;if(!group||phase!=="hit"){lastEffectToken="";els.effect.dataset.parts="";els.bursts.forEach(b=>b.classList.remove("is-active"));return}const token=String(group[0].time);if(token===lastEffectToken)return;lastEffectToken=token;const parts=[...new Set(group.map(n=>n.part))],points=parts.map(p=>EFFECT_POINTS[p]).filter(Boolean).slice(0,3);els.effect.dataset.parts=parts.join("+");els.bursts.forEach((burst,index)=>{burst.classList.remove("is-active");const point=points[index];if(!point)return;burst.setAttribute("transform",`translate(${point[0]} ${point[1]})`);void burst.getBoundingClientRect();burst.classList.add("is-active")})}
export async function initCharacterPrototype(){els.root=document.getElementById("characterBackdrop");els.drum=document.getElementById("drumLayer");els.character=document.getElementById("characterLayer");els.label=document.getElementById("characterPoseLabel");els.effect=document.getElementById("effectLayer");els.bursts=[document.getElementById("effectPrimary"),document.getElementById("effectSecondary"),document.getElementById("effectTertiary")].filter(Boolean);if(!els.root||!els.drum||!els.character)return;els.drum.src=assetUrl(DRUM);els.character.src=assetUrl(ASSET_ROOT+"/layers/character/base/neutral.png");const fail=e=>{markAssetIssue(e?.target?.src||"dom-image-load");els.root.dataset.state="asset-warning"};els.drum.addEventListener("error",fail);els.character.addEventListener("error",fail);try{const [notesResponse,inventoryResponse,limbResponse]=await Promise.all([fetch(PROTOTYPE_URL,{cache:"no-store"}),fetch(INVENTORY_URL,{cache:"no-store"}),fetch(LIMB_URL,{cache:"no-store"})]);if(!notesResponse.ok)throw new Error("prototype HTTP "+notesResponse.status);if(!inventoryResponse.ok)throw new Error("inventory HTTP "+inventoryResponse.status);if(!limbResponse.ok)throw new Error("limb HTTP "+limbResponse.status);const [json,inventory,limbData]=await Promise.all([notesResponse.json(),inventoryResponse.json(),limbResponse.json()]);const limbMap=new Map((limbData.assignments||[]).map(item=>[[Number(item.time).toFixed(6),item.part||""].join("|"),item.limb]));for(const note of json.notes||[]){const resolved=limbMap.get(noteIdentity(note));if(resolved)note.limb=resolved}const startMeasure=Number(inventory.runtimeScope?.measureStart??DEFAULT_MEASURE_START),endMeasure=Number(inventory.runtimeScope?.measureEnd??DEFAULT_MEASURE_END);if(!Number.isInteger(startMeasure)||!Number.isInteger(endMeasure)||endMeasure<startMeasure)throw new Error("invalid inventory runtimeScope");const scopedNotes=(json.notes||[]).filter(note=>note.measure>=startMeasure&&note.measure<=endMeasure),groups=groupNotes(scopedNotes);validatePrototypeCoverage(inventory,scopedNotes,groups);data={...json,groups,frames:inventory.requiredFrames||{},frameMap:inventory.runtimeFrameMap||{},phaseFrameMap:inventory.runtimePhaseFrameMap||{},motionTiming:inventory.motionTiming||{},fallbackKeys:new Set(inventory.runtimeFallbackKeys||[]),startMeasure,endMeasure,prototypeEndTime:Math.max(...scopedNotes.map(note=>note.time),0)+.35};const sources=[
  DRUM,
  ...[...new Set(Object.values(data.frames).map(frame=>ASSET_ROOT+"/"+frame.path))]
];let loadedSources=0;window.dispatchEvent(new CustomEvent("dtx-preload-progress",{detail:{kind:"character",done:0,total:sources.length,ratio:0,label:"人物画像を読み込み中"}}));const preloadResults=await Promise.allSettled(sources.map(async src=>{try{return await loadImage(src)}finally{loadedSources++;window.dispatchEvent(new CustomEvent("dtx-preload-progress",{detail:{kind:"character",done:loadedSources,total:sources.length,ratio:sources.length?loadedSources/sources.length:1,label:"人物画像を読み込み中"}}))}}));const failedSources=preloadResults.map((result,index)=>result.status==="rejected"?sources[index]:null).filter(Boolean);window.dispatchEvent(new CustomEvent("dtx-preload-progress",{detail:{kind:"character",done:sources.length,total:sources.length,ratio:1,label:failedSources.length?"人物画像の一部で読み込み失敗":"人物画像の読み込み完了",failed:failedSources.length}}));if(failedSources.length){markAssetIssue(failedSources.join(","));console.warn("character asset preload warning",failedSources)}ready=true;els.root.classList.add("character-ready");els.root.dataset.state=failedSources.length?"ready-with-asset-warning":"ready";els.root.dataset.scope=`${startMeasure}-${endMeasure}`;els.root.dataset.runtimeScope=`${startMeasure}-${endMeasure}`;els.root.dataset.noteCount=String(scopedNotes.length);els.root.dataset.groupCount=String(groups.length);updateDevHud("preload:ok")}catch(err){window.dispatchEvent(new CustomEvent("dtx-preload-progress",{detail:{kind:"character",ratio:1,label:"人物画像の初期化に失敗",failed:1}}));console.warn("character prototype initialization warning",err);els.root.dataset.state="init-warning";els.root.dataset.initError=String(err?.message||err);updateDevHud("init:warning");ready=true;els.root.classList.add("character-ready","asset-warning")}addEventListener("dtx-chart-change",e=>{activeSong=String(e.detail?.name||"").toLowerCase().includes("luna");els.root.classList.toggle("active",activeSong)})}
export function updateCharacterPrototype(time,chartName="",playbackRate=1){if(!els.root)return;els.root.dataset.currentTime=Number(time||0).toFixed(6);activeSong=String(chartName||"").toLowerCase().includes("luna");const provisionalEnd=Number(data?.prototypeEndTime??10.47),inWindow=Number(time)>=0&&Number(time)<=provisionalEnd;els.root.classList.toggle("active",activeSong&&inWindow);els.root.dataset.active=String(activeSong&&inWindow);if(!ready||!data)return;if(!activeSong||!inWindow){triggerEffect(null,"neutral");return}const g=findGroupAt(time,playbackRate);if(!g){els.root.dataset.measure="";els.root.dataset.fallback="false";els.root.dataset.fallbackReason="";els.root.dataset.animationKey="neutral";els.root.dataset.limbs="";triggerEffect(null,"neutral");setFrame(data.frames.neutral.path,"NEUTRAL","neutral");return}const phase=phaseFor(g,time,playbackRate),resolvedKey=keyFor(g),fallback=fallbackInfo(g);els.root.dataset.measure=String(g[0]?.measure??"");els.root.dataset.fallback=String(fallback.fallback);els.root.dataset.fallbackReason=fallback.reason;els.root.dataset.animationKey=resolvedKey;els.root.dataset.limbs=g.map(n=>n.part+":"+handForNote(n)).join(",");const asset=assetFor(g,phase);const parts=[...new Set(g.map(n=>n.part))].sort().join("+"),hand=g.map(n=>handForNote(n)).filter(Boolean).join("/");triggerEffect(g,phase);setFrame(asset,phase==="neutral"?"NEUTRAL":parts+(hand?" · "+hand:"")+" · "+phase.toUpperCase(),phase);updateDevHud()}

// Public runtime QA hook. Enabled only with ?qa=1; normal users are unaffected.
if(new URLSearchParams(location.search).get("qa")==="1"){
  window.__DTX_CHARACTER_QA__={snapshot(){const r=document.getElementById("characterBackdrop"),ch=document.getElementById("characterLayer"),dr=document.getElementById("drumLayer");return {ready,activeSong,currentTime:r?.dataset.currentTime||"",measure:r?.dataset.measure||"",animationKey:r?.dataset.animationKey||"",phase:r?.dataset.phase||"",frame:r?.dataset.frame||"",limbs:r?.dataset.limbs||"",runtimeScope:r?.dataset.runtimeScope||r?.dataset.scope||"",assetWarning:r?.dataset.assetIssue||"",initError:r?.dataset.initError||"",state:r?.dataset.state||"",character:{src:ch?.src||"",complete:!!ch?.complete,naturalWidth:ch?.naturalWidth||0,naturalHeight:ch?.naturalHeight||0},drum:{src:dr?.src||"",complete:!!dr?.complete,naturalWidth:dr?.naturalWidth||0,naturalHeight:dr?.naturalHeight||0}};}};
}
