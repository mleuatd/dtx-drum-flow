const RATE_NAMES = ["quarter","eighth","sixteenth"];

export function inferSubdivision(deltaSec, bpm){
  if(!Number.isFinite(deltaSec) || deltaSec<=0 || !Number.isFinite(bpm) || bpm<=0) return "eighth";
  const quarter=60/bpm;
  const ratios={quarter:quarter,eighth:quarter/2,sixteenth:quarter/4};
  let best="eighth",err=Infinity;
  for(const [name,dur] of Object.entries(ratios)){
    const e=Math.abs(deltaSec-dur)/dur;
    if(e<err){err=e;best=name}
  }
  return best;
}

export function groupSimultaneous(notes, windowMs=8){
  const sorted=[...notes].sort((a,b)=>a.time-b.time);
  const groups=[];
  for(const note of sorted){
    const last=groups.at(-1);
    if(last && Math.abs(note.time-last[0].time)*1000<=windowMs) last.push(note);
    else groups.push([note]);
  }
  return groups;
}

export function createAnimationResolver(config){
  const state={lastTimeByPart:new Map(), repeatIndexByPart:new Map()};

  function explicit(note){
    const a=note?.animation;
    if(!a) return null;
    if(a.lockFrame && a.frame) return {frame:a.frame,phase:a.phase||"hit",hand:a.hand||null,rule:a.rule||"explicit"};
    return a.rule?{rule:a.rule,phase:a.phase||"hit",hand:a.hand||null,frame:a.frame||null}:null;
  }

  function comboKey(group){
    const parts=[...new Set(group.map(n=>n.part))];
    const exact=parts.sort().join("+");
    if(config.simultaneous?.[exact]) return exact;
    const tom=parts.some(p=>["HT","LT","FT"].includes(p));
    const cym=parts.some(p=>["LC","RC","RD"].includes(p));
    return tom&&cym&&config.simultaneous?.["TOM+CYMBAL"]?"TOM+CYMBAL":null;
  }

  function resolve(group,bpm){
    const first=group[0];
    const ex=group.map(explicit).find(Boolean);
    if(ex) return ex;

    const ck=comboKey(group);
    if(ck){
      const c=config.simultaneous[ck];
      return {rule:c.rule,frame:c.character,phase:"hit",hand:null,combo:ck};
    }

    const part=first.part;
    const prev=state.lastTimeByPart.get(part);
    const delta=Number.isFinite(prev)?first.time-prev:null;
    const rate=inferSubdivision(delta,bpm);
    const partRule=config.parts?.[part]?.[rate] || config.parts?.[part]?.eighth || config.parts?.[part]?.quarter;
    if(!partRule) return {rule:"neutral",frame:"base/neutral",phase:"hit",hand:null,rate};

    const repeat=(state.repeatIndexByPart.get(part)||0);
    const sticking=partRule.sticking||["R"];
    const hand=sticking[repeat%sticking.length]||sticking[0]||null;
    state.repeatIndexByPart.set(part,repeat+1);
    state.lastTimeByPart.set(part,first.time);

    let frame=partRule.frames?.find(f=>f.endsWith(`hit_${String(hand).toLowerCase()}`))
      || partRule.frames?.find(f=>f.includes("/hit"))
      || partRule.frames?.[0]
      || null;

    return {rule:partRule.rule,frame,phase:"hit",hand,rate};
  }

  function reset(){
    state.lastTimeByPart.clear();
    state.repeatIndexByPart.clear();
  }

  return {resolve,reset};
}
