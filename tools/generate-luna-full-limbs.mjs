import fs from "node:fs";

const chart=JSON.parse(fs.readFileSync("site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json","utf8"));
const prefix=JSON.parse(fs.readFileSync("site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json","utf8"));
const rules=JSON.parse(fs.readFileSync("character-assets/prototypes/luna_say_maybe_16m/hand_rules.json","utf8"));
const notes=chart.notes.map((n,i)=>({...n,_i:i})).sort((a,b)=>a.time-b.time||a._i-b._i);
const EPS=.008, RAPID=.13, TOM_RESTART=.36;
const handParts=new Set(["LC","HH","SN","HT","LT","FT","RC","RD"]);
const footParts=new Set(["LP","LB","BD"]);
const cymbalParts=new Set(["LC","HH","RC","RD"]);
const tomParts=new Set(["HT","LT","FT"]);
const pref={LC:"R",HH:"R",SN:"L",HT:"R",LT:"R",FT:"R",RC:"R",RD:"R",LP:"LF",LB:"LF",BD:"RF"};
const key=n=>Number(n.time).toFixed(6)+"|"+n.part;
const prefixMap=new Map(prefix.assignments.map(a=>[Number(a.time).toFixed(6)+"|"+a.part,a.limb]));

function groups(src){
  const out=[];
  for(const n of src){const g=out.at(-1); if(g&&Math.abs(g[0].time-n.time)<=EPS)g.push(n); else out.push([n]);}
  return out;
}
const allGroups=groups(notes);
const groupByTime=new Map(allGroups.map(g=>[Number(g[0].time).toFixed(6),g]));

function baseAssignments(src){
  const a=new Map();
  let lastTomTime=-Infinity,tomIndex=0;
  for(const n of src){
    if(n.part==="BD")a.set(key(n),"RF");
    else if(n.part==="LP"||n.part==="LB")a.set(key(n),"LF");
    else if(n.part==="SN")a.set(key(n),"L");
    else if(n.part==="HH"||n.part==="LC"||n.part==="RC"||n.part==="RD")a.set(key(n),"R");
    else if(tomParts.has(n.part)){
      if(n.time-lastTomTime>TOM_RESTART)tomIndex=0;
      a.set(key(n),tomIndex%2===0?"R":"L");
      tomIndex++; lastTomTime=n.time;
    } else a.set(key(n),null);
  }
  return a;
}

function rapidPhrases(src,part){
  const p=src.filter(n=>n.part===part),out=[]; let cur=[];
  for(const n of p){
    if(!cur.length){cur=[n];continue;}
    if(n.time-cur.at(-1).time<=RAPID+1e-9)cur.push(n);
    else {if(cur.length>=2)out.push(cur);cur=[n];}
  }
  if(cur.length>=2)out.push(cur);
  return out;
}
function nearestOtherHandBefore(time,excludePart){
  for(let i=notes.length-1;i>=0;i--){const n=notes[i];if(n.time>=time-EPS)continue;if(time-n.time>.16)break;if(handParts.has(n.part)&&n.part!==excludePart)return n;}
  return null;
}
function nearestOtherHandAfter(time,excludePart){
  for(const n of notes){if(n.time<=time+EPS)continue;if(n.time-time>.16)break;if(handParts.has(n.part)&&n.part!==excludePart)return n;}
  return null;
}
function candidatePhraseHands(len,start){return Array.from({length:len},(_,i)=>i%2===0?start:(start==="R"?"L":"R"))}

function scoreSnPhrase(phrase,hands,assign){
  let cost=hands[0]==="R"?0:1;
  const prev=nearestOtherHandBefore(phrase[0].time,"SN");
  const next=nearestOtherHandAfter(phrase.at(-1).time,"SN");
  if(prev && phrase[0].time-prev.time<=.13 && hands[0]===assign.get(key(prev)))cost+=4;
  if(next && next.time-phrase.at(-1).time<=.13 && hands.at(-1)===assign.get(key(next)))cost+=10;
  for(let i=0;i<phrase.length;i++){
    const g=groupByTime.get(Number(phrase[i].time).toFixed(6))||[];
    for(const other of g){
      if(other.part==="SN"||!handParts.has(other.part))continue;
      if(assign.get(key(other))===hands[i])cost+=100;
    }
  }
  return cost;
}
function applyRapidSn(assign){
  const decisions=[];
  for(const phrase of rapidPhrases(notes,"SN")){
    const r=candidatePhraseHands(phrase.length,"R"),l=candidatePhraseHands(phrase.length,"L");
    const sr=scoreSnPhrase(phrase,r,assign),sl=scoreSnPhrase(phrase,l,assign);
    const chosen=sr<=sl?r:l;
    phrase.forEach((n,i)=>assign.set(key(n),chosen[i]));
    decisions.push({start:phrase[0].time,end:phrase.at(-1).time,measureStart:phrase[0].measure,measureEnd:phrase.at(-1).measure,count:phrase.length,startHand:chosen[0],sequence:chosen.join(""),scoreR:sr,scoreL:sl});
  }
  return decisions;
}
function applyRapidHH(assign){
  const decisions=[];
  for(const phrase of rapidPhrases(notes,"HH")){
    let seq=candidatePhraseHands(phrase.length,"R");
    phrase.forEach((n,i)=>assign.set(key(n),seq[i]));
    decisions.push({start:phrase[0].time,end:phrase.at(-1).time,count:phrase.length});
  }
  return decisions;
}
function resolveGroups(assign){
  const fixes=[],unresolved=[];
  for(const g of allGroups){
    const hs=g.filter(n=>handParts.has(n.part));
    if(hs.length<=1)continue;
    if(hs.length>2){unresolved.push({time:g[0].time,measure:g[0].measure,reason:"MORE_THAN_TWO_HAND_NOTES",notes:hs.map(n=>({part:n.part,limb:assign.get(key(n))}))});continue;}
    const [a,b]=hs,la=assign.get(key(a)),lb=assign.get(key(b));
    if(la!==lb)continue;
    const parts=new Set([a.part,b.part]);
    if(parts.has("SN") && [...parts].some(p=>cymbalParts.has(p))){
      for(const n of hs)assign.set(key(n),n.part==="SN"?"L":"R");
      fixes.push({time:g[0].time,measure:g[0].measure,policy:"SN+Cymbal => SN=L,cymbal=R",notes:hs.map(n=>({part:n.part,limb:assign.get(key(n))}))});
    } else if(parts.has("SN") && [...parts].some(p=>tomParts.has(p))){
      for(const n of hs)assign.set(key(n),n.part==="SN"?"L":"R");
      fixes.push({time:g[0].time,measure:g[0].measure,policy:"SN+Tom => SN=L,tom=R",notes:hs.map(n=>({part:n.part,limb:assign.get(key(n))}))});
    } else if(hs.every(n=>tomParts.has(n.part))){
      const order={HT:0,LT:1,FT:2}; const s=[...hs].sort((x,y)=>order[x.part]-order[y.part]);
      assign.set(key(s[0]),"L");assign.set(key(s[1]),"R");
      fixes.push({time:g[0].time,measure:g[0].measure,policy:"Two toms => leftmost=L,rightmost=R",notes:hs.map(n=>({part:n.part,limb:assign.get(key(n))}))});
    } else {
      // keep the more strongly right-biased cymbal on R, move the other hand note to L.
      const priority=n=>({RC:5,RD:5,HH:4,LC:3,FT:2,LT:2,HT:2,SN:1}[n.part]||0);
      const right=priority(a)>=priority(b)?a:b,left=right===a?b:a;
      assign.set(key(right),"R");assign.set(key(left),"L");
      fixes.push({time:g[0].time,measure:g[0].measure,policy:"Two-hand uniqueness/minimal preference",notes:hs.map(n=>({part:n.part,limb:assign.get(key(n))}))});
    }
  }
  return {fixes,unresolved};
}
function validate(assign,scopeMin=1,scopeMax=148){
  const missing=[],sameLimb=[],rapidRepeat=[];
  const scoped=notes.filter(n=>n.measure>=scopeMin&&n.measure<=scopeMax);
  for(const n of scoped)if(!assign.get(key(n)))missing.push({time:n.time,measure:n.measure,part:n.part});
  for(const g of groups(scoped)){
    const used=new Map();
    for(const n of g){const l=assign.get(key(n));if(!l)continue;(used.get(l)||used.set(l,[]).get(l)).push(n);}
    for(const [limb,ns] of used)if(ns.length>1)sameLimb.push({time:g[0].time,measure:g[0].measure,limb,notes:ns.map(n=>n.part)});
  }
  const sns=scoped.filter(n=>n.part==="SN");
  for(let i=1;i<sns.length;i++){const gap=sns[i].time-sns[i-1].time;if(gap<=RAPID+1e-9&&assign.get(key(sns[i]))===assign.get(key(sns[i-1])))rapidRepeat.push({prev:sns[i-1].time,time:sns[i].time,measure:sns[i].measure,limb:assign.get(key(sns[i])),gap});}
  return {missing,sameLimb,rapidRepeat};
}

const predicted=baseAssignments(notes);
const rapidSnDecisions=applyRapidSn(predicted);
const rapidHhDecisions=applyRapidHH(predicted);
const groupResolution=resolveGroups(predicted);
const prefixMismatches=[];
for(const a of prefix.assignments){
  const got=predicted.get(Number(a.time).toFixed(6)+"|"+a.part);
  if(got!==a.limb)prefixMismatches.push({...a,predicted:got});
}

// Use authoritative prefix exactly, predicted v2 rules after M16.
const finalAssign=new Map(predicted);
for(const a of prefix.assignments)finalAssign.set(Number(a.time).toFixed(6)+"|"+a.part,a.limb);
const validation=validate(finalAssign,1,148);
const assignments=notes.map(n=>({time:n.time,measure:n.measure,beatIndex:n.beatIndex,part:n.part,limb:finalAssign.get(key(n))}));
const countByLimb={};for(const a of assignments)countByLimb[a.limb]=(countByLimb[a.limb]||0)+1;
const candidate={
  version:2,chart:"Luna_say_maybe_FINAL_notes.json",
  generatedAt:new Date().toISOString(),
  scope:{measureStart:1,measureEnd:148,noteCount:assignments.length},
  handedness:"right-handed",
  method:"Authoritative M1-16 prefix + researched/project v2 deterministic limb rules for M17-148.",
  rulesSource:"character-assets/prototypes/luna_say_maybe_16m/hand_rules.json",
  assignments
};
const report={
  generatedAt:new Date().toISOString(),
  counts:{notes:assignments.length,...countByLimb},
  prefixRegression:{mismatches:prefixMismatches.length,details:prefixMismatches},
  rapidSnPhrases:{count:rapidSnDecisions.length,decisions:rapidSnDecisions},
  rapidHhPhrases:{count:rapidHhDecisions.length},
  simultaneousResolution:{fixCount:groupResolution.fixes.length,fixes:groupResolution.fixes,unresolved:groupResolution.unresolved},
  validation:{missing:validation.missing.length,sameLimb:validation.sameLimb.length,rapidSameHand:validation.rapidRepeat.length,missingDetails:validation.missing,sameLimbDetails:validation.sameLimb,rapidSameHandDetails:validation.rapidRepeat},
  promotable:prefixMismatches.length===0&&groupResolution.unresolved.length===0&&validation.missing.length===0&&validation.sameLimb.length===0&&validation.rapidRepeat.length===0
};
fs.mkdirSync("limb-artifacts",{recursive:true});
fs.writeFileSync("limb-artifacts/Luna_say_maybe_full_limbs_CANDIDATE.json",JSON.stringify(candidate,null,2)+"\n");
fs.writeFileSync("limb-artifacts/Luna_say_maybe_full_limbs_VALIDATION.json",JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({promotable:report.promotable,counts:report.counts,prefixMismatches:report.prefixRegression.mismatches,rapidSnPhrases:report.rapidSnPhrases.count,simultaneousFixes:report.simultaneousResolution.fixCount,unresolvedGroups:report.simultaneousResolution.unresolved.length,validation:report.validation},null,2));
if(!report.promotable)process.exitCode=1;
