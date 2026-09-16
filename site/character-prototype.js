const PROTOTYPE_URL="./character-assets/prototypes/luna_say_maybe_16m/Luna_say_maybe_16m_animation.json";
const INVENTORY_URL="./character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json";
const ASSET_ROOT="./character-assets";
const DRUM="./character-assets/layers/drum/drum_base.png";

let data=null,lastKey="",lastEffectToken="",ready=false,activeSong=false;
const els={root:null,drum:null,character:null,label:null,effect:null,bursts:[]};
const EFFECT_POINTS={HH:[255,465],SN:[570,520],BD:[505,790],RC:[1090,195],RD:[1070,370]};

function loadImage(src){
  return new Promise((resolve,reject)=>{
    const image=new Image();
    image.onload=()=>resolve(src);
    image.onerror=()=>reject(new Error("image HTTP/load failure: "+src));
    image.src=src;
  });
}

function groupNotes(notes){
  const groups=[];
  for(const n of notes){
    const g=groups.at(-1);
    if(g&&Math.abs(n.time-g[0].time)<=.008)g.push(n);else groups.push([n]);
  }
  return groups;
}
function keyFor(group){
  const parts=[...new Set(group.map(n=>n.part))].sort();
  if(parts.length>1){
    const combo=parts.join("+");
    if(data?.frameMap?.[combo+":*"])return combo+":*";
  }
  const n=group[0],hand=n.animation?.hand||"R";
  return n.part+":"+hand;
}
function assetFor(group,phase="hit"){
  if(phase==="neutral")return data?.frames?.neutral?.path||"layers/character/base/neutral.png";
  const key=keyFor(group);
  const phases=data?.phaseFrameMap?.[key];
  const frameId=phases?.[phase]||data?.frameMap?.[key]||"neutral";
  return data?.frames?.[frameId]?.path||"layers/character/base/neutral.png";
}
function setFrame(path,label="",phase="neutral"){
  if(!els.character)return;
  const src=ASSET_ROOT+"/"+path;
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
  const points=parts.map(part=>EFFECT_POINTS[part]).filter(Boolean).slice(0,2);
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
  els.bursts=[document.getElementById("effectPrimary"),document.getElementById("effectSecondary")].filter(Boolean);
  if(!els.root||!els.drum||!els.character)return;
  els.drum.src=DRUM;
  els.character.src=ASSET_ROOT+"/layers/character/base/neutral.png";
  const fail=()=>{els.root.classList.add("assets-missing");els.root.dataset.state="assets-missing"};
  els.drum.addEventListener("error",fail,{once:true});
  els.character.addEventListener("error",fail,{once:true});
  try{
    const [notesResponse,inventoryResponse]=await Promise.all([
      fetch(PROTOTYPE_URL,{cache:"no-store"}),
      fetch(INVENTORY_URL,{cache:"no-store"})
    ]);
    if(!notesResponse.ok)throw new Error("prototype HTTP "+notesResponse.status);
    if(!inventoryResponse.ok)throw new Error("inventory HTTP "+inventoryResponse.status);
    const [json,inventory]=await Promise.all([notesResponse.json(),inventoryResponse.json()]);
    const startMeasure=Number(inventory.runtimeScope?.measureStart||1);
    const endMeasure=Number(inventory.runtimeScope?.measureEnd||8);
    const scopedNotes=(json.notes||[]).filter(note=>note.measure>=startMeasure&&note.measure<=endMeasure);
    const groups=groupNotes(scopedNotes);
    data={
      ...json,
      groups,
      frames:inventory.requiredFrames||{},
      frameMap:inventory.runtimeFrameMap||{},
      phaseFrameMap:inventory.runtimePhaseFrameMap||{},
      motionTiming:inventory.motionTiming||{},
      startMeasure,
      endMeasure,
      prototypeEndTime:Math.max(...scopedNotes.map(note=>note.time),0)+.35
    };
    const usedFrameIds=new Set(["neutral"]);
    for(const group of groups){
      const parts=[...new Set(group.map(note=>note.part))].sort();
      const key=parts.length>1?parts.join("+")+":*":parts[0]+":"+(group[0].animation?.hand||"R");
      usedFrameIds.add(data.frameMap[key]||"neutral");
      Object.values(data.phaseFrameMap[key]||{}).forEach(id=>usedFrameIds.add(id));
    }
    const sources=[DRUM,...[...usedFrameIds].map(id=>ASSET_ROOT+"/"+data.frames[id].path)];
    await Promise.all(sources.map(loadImage));
    ready=true;
    els.root.classList.add("character-ready");
    els.root.dataset.state="ready";
    els.root.dataset.scope=`${startMeasure}-${endMeasure}`;
  }catch(err){
    console.warn("character prototype disabled",err);
    fail();
  }
  addEventListener("dtx-chart-change",e=>{
    activeSong=String(e.detail?.name||"").toLowerCase().includes("luna");
    els.root.classList.toggle("active",activeSong);
  });
}
export function updateCharacterPrototype(time,chartName=""){
  if(!ready||!els.root)return;
  activeSong=String(chartName||"").toLowerCase().includes("luna");
  const inWindow=Number(time)>=0&&Number(time)<=data.prototypeEndTime;
  els.root.classList.toggle("active",activeSong&&inWindow);
  els.root.dataset.active=String(activeSong&&inWindow);
  if(!activeSong||!inWindow){triggerEffect(null,"neutral");return}
  const g=findGroupAt(time);
  if(!g){triggerEffect(null,"neutral");setFrame(data?.frames?.neutral?.path||"layers/character/base/neutral.png","NEUTRAL","neutral");return}
  const phase=phaseFor(g,time);
  const asset=assetFor(g,phase);
  if(phase==="neutral"){
    triggerEffect(null,"neutral");
    setFrame(asset,"NEUTRAL","neutral");
    return;
  }
  const parts=[...new Set(g.map(n=>n.part))].sort().join("+");
  const hand=g.map(n=>n.animation?.hand).filter(Boolean).join("/");
  triggerEffect(g,phase);
  setFrame(asset,parts+(hand?" · "+hand:"")+" · "+phase.toUpperCase(),phase);
}
