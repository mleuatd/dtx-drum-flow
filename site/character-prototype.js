const PROTOTYPE_URL="./charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json";
const PROTOTYPE_MEASURE_START=1;
const PROTOTYPE_MEASURE_END=8;
const LIMB_URL="./charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json";
const INVENTORY_URL="./character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json";
const ASSET_ROOT="./character-assets";
const ASSET_VERSION="20260917-keyfix-r7";
const DRUM="./character-assets/layers/drum/drum_base.png";
const assetUrl=src=>src+(src.includes("?")?"&":"?")+"v="+ASSET_VERSION;

let data=null,lastKey="",lastEffectToken="",ready=false,activeSong=false;
const els={root:null,drum:null,character:null,label:null,effect:null,bursts:[]};
function updateDevHud(extra=""){
  const hud=document.getElementById("devBuildHud");
  if(!hud)return;
  const root=document.getElementById("characterBackdrop");
  const lines=[
    "BUILD 20260917-devhud-r6",
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
const EFFECT_POINTS={HH:[255,465],SN:[570,520],BD:[505,790],HT:[690,455],LT:[790,510],FT:[910,585],RC:[1090,195],RD:[1070,370]};

function loadImage(src){
  return new Promise((resolve,reject)=>{
    const image=new Image();
    image.onload=()=>resolve(src);
    image.onerror=()=>reject(new Error("image HTTP/load failure: "+src));
    image.src=assetUrl(src);
  });
}
function markAssetIssue(src){
  if(!els.root)return;
  els.root.dataset.assetIssue=src||"unknown";
  els.root.classList.add("asset-warning");
}

function groupNotes(notes){
  const groups=[];
  for(const n of notes){
    const g=groups.at(-1);
    if(g&&Math.abs(n.time-g[0].time)<=.008)g.push(n);else groups.push([n]);
  }
  return groups;
}
function noteIdentity(note){
  return [Number(note?.time).toFixed(6),note?.part||""].join("|");
}
function handForNote(note){
  if(note?.limb)return note.limb;
  if(note?.animation?.limb)return note.animation.limb;
  if(note?.animation?.hand)return note.animation.hand;
  if(note?.animation?.foot)return note.animation.foot;
  if(note?.part==="SN")return "L";
  if(note?.part==="BD"||note?.part==="LB")return "RF";
  if(note?.part==="LP")return "LF";
  return "R";
}
function fallbackInfo(group){
  if(!group?.length)return {fallback:false,reason:""};
  const key=keyFor(group);
  if(!data?.frameMap?.[key])return {fallback:true,reason:"missing-exact-frame"};
  if(data?.fallbackKeys?.has(key))return {fallback:true,reason:"declared-fallback-key"};
  return {fallback:false,reason:""};
}
function keyFor(group,frameMap=data?.frameMap){
  const parts=[...new Set(group.map(n=>n.part))].sort();
  if(parts.length>1){
    const combo=parts.join("+")+":*";
    if(frameMap?.[combo])return combo;
  }
  const n=group[0];
  return n.part+":"+handForNote(n);
}
function assetFor(group,phase="hit"){
  if(phase==="neutral")return data?.frames?.neutral?.path||"layers/character/base/neutral.png";
  const key=keyFor(group);
  const phases=data?.phaseFrameMap?.[key];
  const frameId=phases?.[phase]||data?.frameMap?.[key]||"neutral";
  return data?.frames?.[frameId]?.path||"layers/character/base/neutral.png";
}
function validatePrototypeCoverage(inventory,scopedNotes,groups){
  const scope=inventory.runtimeScope||{};
  const expectedNotes=Number(scope.noteCount||0);
  const expectedGroups=Number(scope.groupCount||0);
  if(scopedNotes.length!==expectedNotes)throw new Error(`prototype note count ${scopedNotes.length} != ${expectedNotes}`);
  if(groups.length!==expectedGroups)throw new Error(`prototype group count ${groups.length} != ${expectedGroups}`);
  const unresolvedLimbs=scopedNotes.filter(note=>!note.limb);
  if(unresolvedLimbs.length)throw new Error(`prototype limb assignments missing: ${unresolvedLimbs.length}`);
  const expectedKeys=new Set(scope.expectedKeys||[]);
  const actualKeys=new Set();
  for(const group of groups){
    const key=keyFor(group,inventory.runtimeFrameMap);
    actualKeys.add(key);
    if(!inventory.runtimeFrameMap?.[key])throw new Error(`prototype frame missing for ${key} at ${group[0].time}`);
    for(const phase of ["prep","hit","rebound"]){
      const frameId=inventory.runtimePhaseFrameMap?.[key]?.[phase];
      if(!frameId||!inventory.requiredFrames?.[frameId])throw new Error(`prototype phase frame missing for ${key}.${phase}`);
    }
  }
  const missing=[...expectedKeys].filter(key=>!actualKeys.has(key));
  const unexpected=[...actualKeys].filter(key=>!expectedKeys.has(key));
  if(missing.length||unexpected.length)throw new Error(`prototype key mismatch missing=${missing.join(",")} unexpected=${unexpected.join(",")}`);
}
function setFrame(path,label="",phase="neutral"){
  if(!els.character)return;
  const src=assetUrl(ASSET_ROOT+"/"+path);
  if(lastKey!==src){lastKey=src;els.character.src=src}
  if(els.label)els.label.textContent=label;
  if(els.root){els.root.dataset.frame=path;els.root.dataset.pose=label;els.root.dataset.phase=phase}
}
function findGroupAt(time){
  if(!data?.groups?.length)return null;
  let previous=null,next=null;
  for(const group of data.groups){
    if(group[0].time<=time)previous=group;
    else{next=group;break}
  }
  const rapidMaxGap=Number(data?.motionTiming?.rapidRepeatMaxGapSeconds??.13);
  if(previous&&next&&next[0].time-previous[0].time<=rapidMaxGap&&keyFor(previous)===keyFor(next)){
    return previous;
  }
  let best=null,bestDt=Infinity;
  for(const g of data.groups){
    const dt=Math.abs(g[0].time-time);
    if(dt<bestDt){bestDt=dt;best=g}
    if(g[0].time>time+.16)break;
  }
  return bestDt<=.13?best:null;
}
function phaseFor(group,time){
  const delta=Number(time)-group[0].time;
  const timing=data?.motionTiming||{};
  const prepBoundary=Number(timing.prepBoundarySeconds??-.028);
  const hitEnd=Number(timing.hitEndSeconds??.038);
  const reboundEnd=Number(timing.reboundEndSeconds??.075);
  const rapidMaxGap=Number(timing.rapidRepeatMaxGapSeconds??.13);
  if(delta<prepBoundary)return "prep";
  if(delta<=hitEnd)return "hit";
  const index=data.groups.indexOf(group);
  const next=data.groups[index+1];
  const nextGap=next?next[0].time-group[0].time:Infinity;
  if(delta>reboundEnd&&nextGap>rapidMaxGap)return "neutral";
  return "rebound";
}
function triggerEffect(group,phase){
  if(!els.effect)return;
  if(!group||phase!=="hit"){
    lastEffectToken="";
    els.effect.dataset.parts="";
    els.bursts.forEach(burst=>burst.classList.remove("is-active"));
    return;
  }
  const token=String(group[0].time);
  if(token===lastEffectToken)return;
  lastEffectToken=token;
  const parts=[...new Set(group.map(note=>note.part))];
  const points=parts.map(part=>EFFECT_POINTS[part]).filter(Boolean).slice(0,3);
  els.effect.dataset.parts=parts.join("+");
  els.bursts.forEach((burst,index)=>{
    burst.classList.remove("is-active");
    const point=points[index];
    if(!point)return;
    burst.setAttribute("transform",`translate(${point[0]} ${point[1]})`);
    void burst.getBoundingClientRect();
    burst.classList.add("is-active");
  });
}
export async function initCharacterPrototype(){
  els.root=document.getElementById("characterBackdrop");
  els.drum=document.getElementById("drumLayer");
  els.character=document.getElementById("characterLayer");
  els.label=document.getElementById("characterPoseLabel");
  els.effect=document.getElementById("effectLayer");
  els.bursts=[document.getElementById("effectPrimary"),document.getElementById("effectSecondary"),document.getElementById("effectTertiary")].filter(Boolean);
  if(!els.root||!els.drum||!els.character)return;
  els.drum.src=assetUrl(DRUM);
  els.character.src=assetUrl(ASSET_ROOT+"/layers/character/base/neutral.png");
  const fail=e=>{markAssetIssue(e?.target?.src||"dom-image-load");els.root.dataset.state="asset-warning"};
  els.drum.addEventListener("error",fail);
  els.character.addEventListener("error",fail);
  try{
    const [notesResponse,inventoryResponse,limbResponse]=await Promise.all([
      fetch(PROTOTYPE_URL,{cache:"no-store"}),
      fetch(INVENTORY_URL,{cache:"no-store"}),
      fetch(LIMB_URL,{cache:"no-store"})
    ]);
    if(!notesResponse.ok)throw new Error("prototype HTTP "+notesResponse.status);
    if(!inventoryResponse.ok)throw new Error("inventory HTTP "+inventoryResponse.status);
    if(!limbResponse.ok)throw new Error("limb HTTP "+limbResponse.status);
    const [json,inventory,limbData]=await Promise.all([notesResponse.json(),inventoryResponse.json(),limbResponse.json()]);
    const limbMap=new Map((limbData.assignments||[]).map(item=>[
      [Number(item.time).toFixed(6),item.part||""].join("|"),
      item.limb
    ]));
    for(const note of json.notes||[]){
      const resolved=limbMap.get(noteIdentity(note));
      if(resolved)note.limb=resolved;
    }
    const startMeasure=PROTOTYPE_MEASURE_START;
    const endMeasure=PROTOTYPE_MEASURE_END;
    const scopedNotes=(json.notes||[]).filter(note=>note.measure>=startMeasure&&note.measure<=endMeasure);
    const groups=groupNotes(scopedNotes);
    validatePrototypeCoverage(inventory,scopedNotes,groups);
    data={
      ...json,
      groups,
      frames:inventory.requiredFrames||{},
      frameMap:inventory.runtimeFrameMap||{},
      phaseFrameMap:inventory.runtimePhaseFrameMap||{},
      motionTiming:inventory.motionTiming||{},
      fallbackKeys:new Set(inventory.runtimeFallbackKeys||[]),
      startMeasure,
      endMeasure,
      prototypeEndTime:Math.max(...scopedNotes.map(note=>note.time),0)+.35
    };
    const usedFrameIds=new Set(["neutral"]);
    for(const group of groups){
      const key=keyFor(group);
      usedFrameIds.add(data.frameMap[key]||"neutral");
      Object.values(data.phaseFrameMap[key]||{}).forEach(id=>usedFrameIds.add(id));
    }
    const sources=[DRUM,...[...usedFrameIds].map(id=>ASSET_ROOT+"/"+data.frames[id].path)];
    const preloadResults=await Promise.allSettled(sources.map(loadImage));
    const failedSources=preloadResults
      .map((result,index)=>result.status==="rejected"?sources[index]:null)
      .filter(Boolean);
    if(failedSources.length){
      markAssetIssue(failedSources.join(","));
      console.warn("character asset preload warning",failedSources);
    }
    ready=true;
    els.root.classList.add("character-ready");
    els.root.dataset.state=failedSources.length?"ready-with-asset-warning":"ready";
    els.root.dataset.scope=`${startMeasure}-${endMeasure}`;
    els.root.dataset.noteCount=String(scopedNotes.length);
    els.root.dataset.groupCount=String(groups.length);updateDevHud("preload:ok");
  }catch(err){
    console.warn("character prototype initialization warning",err);
    els.root.dataset.state="init-warning";
    els.root.dataset.initError=String(err?.message||err);updateDevHud("init:warning");
    ready=true;
    els.root.classList.add("character-ready","asset-warning");
  }
  addEventListener("dtx-chart-change",e=>{
    activeSong=String(e.detail?.name||"").toLowerCase().includes("luna");
    els.root.classList.toggle("active",activeSong);
  });
}
export function updateCharacterPrototype(time,chartName=""){
  if(!els.root)return;
  activeSong=String(chartName||"").toLowerCase().includes("luna");
  const provisionalEnd=Number(data?.prototypeEndTime??17.37);
  const inWindow=Number(time)>=0&&Number(time)<=provisionalEnd;
  els.root.classList.toggle("active",activeSong&&inWindow);
  els.root.dataset.active=String(activeSong&&inWindow);
  if(!ready||!data)return;
  if(!activeSong||!inWindow){triggerEffect(null,"neutral");return}
  const g=findGroupAt(time);
  if(!g){els.root.dataset.fallback="false";els.root.dataset.fallbackReason="";els.root.dataset.animationKey="neutral";els.root.dataset.limbs="";triggerEffect(null,"neutral");setFrame(data?.frames?.neutral?.path||"layers/character/base/neutral.png","NEUTRAL","neutral");return}
  const phase=phaseFor(g,time);
  const resolvedKey=keyFor(g);
  const fallback=fallbackInfo(g);
  els.root.dataset.fallback=String(fallback.fallback);
  els.root.dataset.fallbackReason=fallback.reason;
  els.root.dataset.animationKey=resolvedKey;
  els.root.dataset.limbs=g.map(n=>n.part+":"+handForNote(n)).join(",");
  const asset=assetFor(g,phase);
  if(phase==="neutral"){
    triggerEffect(null,"neutral");
    setFrame(asset,"NEUTRAL","neutral");
    return;
  }
  const parts=[...new Set(g.map(n=>n.part))].sort().join("+");
  const hand=g.map(n=>handForNote(n)).filter(Boolean).join("/");
  triggerEffect(g,phase);
  setFrame(asset,parts+(hand?" · "+hand:"")+" · "+phase.toUpperCase(),phase);updateDevHud();
}
