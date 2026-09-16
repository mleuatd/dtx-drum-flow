const PROTOTYPE_URL="./character-assets/prototypes/luna_say_maybe_16m/Luna_say_maybe_16m_animation.json";
const INVENTORY_URL="./character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json";
const ASSET_ROOT="./character-assets";
const DRUM="./character-assets/layers/drum/drum_base.png";

let data=null,lastKey="",ready=false,activeSong=false;
const els={root:null,drum:null,character:null,label:null};

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
function assetFor(group){
  const key=keyFor(group);
  const frameId=data?.frameMap?.[key]||"neutral";
  return data?.frames?.[frameId]?.path||"layers/character/base/neutral.png";
}
function setFrame(path,label=""){
  if(!els.character)return;
  const src=ASSET_ROOT+"/"+path;
  if(lastKey===src)return;
  lastKey=src;
  els.character.src=src;
  if(els.label)els.label.textContent=label;
}
function findGroupAt(time){
  if(!data?.groups?.length)return null;
  let best=null,bestDt=Infinity;
  for(const g of data.groups){
    const dt=Math.abs(g[0].time-time);
    if(dt<bestDt){bestDt=dt;best=g}
    if(g[0].time>time+.16)break;
  }
  return bestDt<=.13?best:null;
}
export async function initCharacterPrototype(){
  els.root=document.getElementById("characterBackdrop");
  els.drum=document.getElementById("drumLayer");
  els.character=document.getElementById("characterLayer");
  els.label=document.getElementById("characterPoseLabel");
  if(!els.root||!els.drum||!els.character)return;
  els.drum.src=DRUM;
  els.character.src=ASSET_ROOT+"/layers/character/base/neutral.png";
  const fail=()=>els.root.classList.add("assets-missing");
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
    data={
      ...json,
      groups:groupNotes(json.notes||[]),
      frames:inventory.requiredFrames||{},
      frameMap:inventory.runtimeFrameMap||{}
    };
    ready=true;
  }catch(err){
    console.warn("character prototype disabled",err);
  }
  addEventListener("dtx-chart-change",e=>{
    activeSong=String(e.detail?.name||"").toLowerCase().includes("luna");
    els.root.classList.toggle("active",activeSong);
  });
}
export function updateCharacterPrototype(time,chartName=""){
  if(!ready||!els.root)return;
  activeSong=String(chartName||"").toLowerCase().includes("luna");
  els.root.classList.toggle("active",activeSong);
  if(!activeSong)return;
  const g=findGroupAt(time);
  if(!g){setFrame(data?.frames?.neutral?.path||"layers/character/base/neutral.png","NEUTRAL");return}
  const asset=assetFor(g);
  const parts=[...new Set(g.map(n=>n.part))].sort().join("+");
  const hand=g.map(n=>n.animation?.hand).filter(Boolean).join("/");
  setFrame(asset,parts+(hand?" · "+hand:""));
}
