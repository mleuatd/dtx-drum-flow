import {makeSample,parseChart} from "./parsers.js?v=20261106-watagashi-gm-r7";
import {decodeAudio,analyzeOnsets,realignNotes} from "./audio-analysis.js";
import {LiveDrumEngine} from "./live-drum-engine.js?v=20260920-chart-preload-r2";
import {applyDrumVoice} from "./drum-note-sound-map.js?v=20260919-audio-final-r21";
import {initCharacterPrototype,updateCharacterPrototype,setDrumGlowNotes} from "./character-prototype.js?v=20261106-short-flash-r4";

const PARTS=["LB","LC","HH","LP","SN","BD","HT","LT","FT","RD","RC"];
const PART_LABEL={LC:"左シンバル",HH:"ハイハット",SN:"スネア",HT:"ハイタム",LT:"ロータム",FT:"フロアタム",RC:"右シンバル",RD:"ライド",LP:"左足HH",LB:"左足BD",BD:"バスドラム"};
const PART_ICON={LC:"◯",HH:"◎",SN:"🥁",HT:"◒",LT:"◓",FT:"◉",RC:"◯",RD:"◌",LP:"⌁",LB:"●",BD:"⬤"};
const $=id=>document.getElementById(id),canvas=$("laneCanvas"),ctx=canvas.getContext("2d");
let chart=makeSample(),time=0,playing=false,audioBuffer=null,onsets=[],audioCtx=null,drumBus=null,liveDrumEngine=null,drumPreloadPromise=null,originalSource=null,schedulerTimer=null,scheduledNodes=[],nextNote=0,nextMetronomeBeat=0,playAnchorCtx=0,playAnchorPerf=0,playAnchorChart=0,playSpeed=1,noteSpeed=1;
const PRELOAD_WEIGHTS={chart:.10,character:.30,drums:.55,original:.05};
const preloadState={
  chart:{ratio:0,label:"譜面",failed:false},
  character:{ratio:0,label:"ドラム画像",failed:false},
  drums:{ratio:0,label:"ドラム音",failed:false},
  original:{ratio:0,label:"原曲確認",failed:false}
};
let startupReady=false,chartNeedsImport=false;
function preloadPercent(){
  let total=0;
  for(const [kind,weight] of Object.entries(PRELOAD_WEIGHTS)){
    total+=Math.max(0,Math.min(1,Number(preloadState[kind]?.ratio)||0))*weight;
  }
  return Math.max(0,Math.min(100,Math.round(total*100)));
}
function renderPreload(){
  const button=$("playPause");if(!button)return;
  const pct=preloadPercent();
  const failed=Object.values(preloadState).some(x=>x.failed);
  startupReady=!failed&&!chartNeedsImport&&Object.values(preloadState).every(x=>Number(x.ratio)>=1);
  button.style.setProperty("--play-load",pct+"%");
  button.disabled=!startupReady;
  button.setAttribute("aria-disabled",String(!startupReady));
  button.classList.toggle("is-loading",!startupReady&&!failed);
  button.classList.toggle("is-ready",startupReady);
  button.classList.toggle("is-error",failed);
  if(failed){
    button.textContent="読み込みエラー";
  }else if(chartNeedsImport){
    button.textContent="わたがし：MIDI譜面を選択";
  }else if(startupReady){
    if(!playing)button.textContent="再生 ▶";
  }else{
    button.textContent="読み込み中 "+pct+"%";
  }
}
function setPreload(kind,ratio,{label="",failed=false}={}){
  if(!preloadState[kind])return;
  preloadState[kind].ratio=Math.max(0,Math.min(1,Number(ratio)||0));
  preloadState[kind].failed=!!failed;
  if(label)preloadState[kind].label=label;
  renderPreload();
}
addEventListener("dtx-preload-progress",e=>{
  const d=e.detail||{};
  if(!preloadState[d.kind])return;
  const ratio=Number.isFinite(Number(d.ratio))?Number(d.ratio):(Number(d.total)>0?Number(d.done||0)/Number(d.total):0);
  setPreload(d.kind,ratio,{label:d.label||"",failed:Number(d.failed||0)>0});
});

const partEls=new Map();
const DEV_MIXER=[
 ["kick","BD/LB"],["snare","SN"],["sideStick","SideStick"],["hihatClosed","HH Closed"],["hihatOpen","HH Open"],["hihatPedal","LP HH"],
 ["tomHigh","HT"],["tomLow","LT"],["tomFloor","FT"],["ride","RD"],["rideBell","Ride Bell"],["crashLeft","LC"],["crashRight","RC"]
];
const DEV_MIXER_DEFAULT={kick:2.5,snare:1,sideStick:.8,hihatClosed:.2,hihatOpen:.15,hihatPedal:1,tomHigh:1,tomLow:1,tomFloor:1.05,ride:.15,rideBell:.15,crashLeft:.15,crashRight:.15};
const devMixerValues={...DEV_MIXER_DEFAULT};
function devMixerText(){
 if(!liveDrumEngine)return "MIX:engine-loading";
 const base=liveDrumEngine.getBaseGains();
 return DEV_MIXER.map(([v,l])=>l+":"+devMixerValues[v].toFixed(2)+" (final "+(base[v]*devMixerValues[v]).toFixed(3)+")").join(String.fromCharCode(10));
}
function refreshDevMixerHud(){const hud=$("devAudioReadout");if(hud)hud.textContent=devMixerText()}
function initDevAudioMixer(){
 const root=$("devAudioMixer");if(!root)return;
 root.innerHTML="";
 for(const [voice,label] of DEV_MIXER){
  const row=document.createElement("div");row.className="dev-audio-row";
  const lab=document.createElement("label");lab.htmlFor="mix-"+voice;lab.textContent=label;
  const input=document.createElement("input");input.type="range";input.id="mix-"+voice;input.min=".10";input.max="2.50";input.step=".05";input.value=String(DEV_MIXER_DEFAULT[voice]??1);input.setAttribute("aria-label",label+" 音量");
  const out=document.createElement("output");out.textContent=Number(input.value).toFixed(2)+"×";
  const test=document.createElement("button");test.type="button";test.className="button dev-audio-test";test.textContent="鳴らす";test.setAttribute("aria-label",label+"を鳴らす");
  test.addEventListener("click",async()=>{await ensureAudio();liveDrumEngine.setUserGain(voice,devMixerValues[voice]);liveDrumEngine.triggerVoice?.(voice,.84,audioCtx.currentTime+.01)});
  input.addEventListener("input",()=>{const n=Number(input.value);devMixerValues[voice]=n;out.textContent=n.toFixed(2)+"×";liveDrumEngine?.setUserGain(voice,n);refreshDevMixerHud()});
  row.append(lab,input,out,test);root.append(row);
 }
 $("devAudioReset")?.addEventListener("click",()=>{for(const [voice] of DEV_MIXER){const input=$("mix-"+voice);if(input){input.value=String(DEV_MIXER_DEFAULT[voice]??1);input.dispatchEvent(new Event("input"))}}});
 refreshDevMixerHud();
}

const clampTime=v=>Math.max(0,Math.min(chart.duration,Number(v)||0));
function fmt(s){s=Math.max(0,s);const m=Math.floor(s/60),sec=(s%60).toFixed(1).padStart(4,"0");return `${m}:${sec}`}
function setStatus(s){$("status").textContent=s}
function downloadText(name,text,type="application/json"){const blob=new Blob([text],{type}),url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),500)}
function chartToJson(){const partKind={BD:"kick",LB:"kick",SN:"snare",HH:"hihat",LP:"hihat",HT:"toms",LT:"toms",FT:"toms",LC:"cymbals",RC:"cymbals",RD:"cymbals"};return {...chart,notes:chart.notes.map(n=>({...n,time:Number(n.time.toFixed(6)),kind:n.kind||partKind[n.part]||"unknown",part:n.part,velocity:Math.round(Math.max(0,Math.min(1,n.velocity??.8))*127),confidence:Number(n.alignConfidence??n.confidence??0)}))}}
function currentSpeed(){return Number($("speed").value)||1}
function setChart(c){pausePlayback(false);chart=c;time=0;nextNote=0;setDrumGlowNotes(c.notes);document.querySelector(".stage")?.classList.toggle("luna-stage",String(c?.name||"").toLowerCase().includes("luna"));$("timeline").max=c.duration;$("duration").textContent=fmt(c.duration);$("chartName").textContent=c.name;$("chartMeta").textContent=`${Math.round(c.bpm)} BPM · ${c.duration.toFixed(1)}秒 · ${c.notes.length.toLocaleString()}ノーツ`;const name=c.name||"";let stage="LUNA / DRUM CHART",badge="LUNA FINAL";if(name.includes("叶えたい")){stage="叶えたい、ことばかり / DRUM CHART";badge="KANAETAI FINAL"}else if(name.includes("一体いつから")){stage="一体いつから / DRUM CHART";badge="ITTAI FINAL"}else if(name.includes("わたがし")){stage="わたがし / DRUM CHART";badge="WATAGASHI"}if($("stageTitle"))$("stageTitle").textContent=stage;if($("chartBadge"))$("chartBadge").textContent=badge;draw();updateTime()}
function updateTime(){$("currentTime").textContent=fmt(time);const mirror=$("currentTimeMirror");if(mirror)mirror.textContent=fmt(time);$("timeline").value=time}
function resize(){const r=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw()}
function draw(){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const lane=w/PARTS.length,isLuna=String(chart?.name||"").toLowerCase().includes("luna");/* Keep chart transparent so the drum illustration shows for every song. */ctx.strokeStyle=isLuna?"rgba(34,54,86,.62)":"#223656";ctx.lineWidth=1;for(let i=1;i<PARTS.length;i++){ctx.beginPath();ctx.moveTo(i*lane,0);ctx.lineTo(i*lane,h);ctx.stroke()}const judgeY=h-36,lookAhead=3.3/noteSpeed;const hitNow=chart.notes.some(n=>Math.abs(n.time-time)<=Math.max(.025,.04/currentSpeed()));ctx.save();ctx.strokeStyle=hitNow?"#ffffff":"#86a7ff";ctx.shadowColor=hitNow?"#9fc5ff":"transparent";ctx.shadowBlur=hitNow?22:0;ctx.lineWidth=hitNow?5:3;ctx.beginPath();ctx.moveTo(0,judgeY);ctx.lineTo(w,judgeY);ctx.stroke();ctx.restore();for(const n of chart.notes){const dt=n.time-time;if(dt<0||dt>lookAhead)continue;const partIndex=PARTS.indexOf(n.part);if(partIndex<0)continue;const x=(partIndex+.5)*lane,y=judgeY-(dt/lookAhead)*(judgeY-20),conf=Number(n.alignConfidence||0);const plateW=Math.max(16,lane*.82),plateH=Math.max(10,Math.min(18,lane*.29)),plateR=Math.min(3.5,plateH*.24);ctx.save();ctx.globalAlpha=conf>0?Math.max(.8,conf):1;ctx.fillStyle=conf>0?(conf>=.65?"#b9f1ff":conf>=.35?"#fff0a5":"#ffbec6"):"#f5fbff";ctx.strokeStyle="#06172d";ctx.lineWidth=2.3;ctx.shadowColor="#86e4ff";ctx.shadowBlur=5;ctx.beginPath();ctx.roundRect(x-plateW/2,y-plateH/2,plateW,plateH,plateR);ctx.fill();ctx.shadowBlur=0;ctx.stroke();ctx.restore()}}
function makeParts(){const root=$("parts");root.innerHTML="";for(const p of PARTS){const el=document.createElement("div");el.className="part";el.innerHTML=`<span class="icon" aria-hidden="true">${PART_ICON[p]}</span><strong>${p}</strong><span class="label">${PART_LABEL[p]}</span>`;root.append(el);partEls.set(p,el)}}
function flash(part){const el=partEls.get(part);if(!el)return;el.classList.add("hit");setTimeout(()=>el.classList.remove("hit"),90)}
function ensureAudioEngine(){
  audioCtx??=new (window.AudioContext||window.webkitAudioContext)({latencyHint:"interactive"});
  if(!drumBus){
    const input=audioCtx.createGain(),comp=audioCtx.createDynamicsCompressor(),out=audioCtx.createGain();
    input.gain.value=1;
    comp.threshold.value=-4;comp.knee.value=12;comp.ratio.value=1.35;comp.attack.value=.01;comp.release.value=.055;
    out.gain.value=1;input.connect(comp);comp.connect(out);out.connect(audioCtx.destination);drumBus=input;
  }
  liveDrumEngine??=new LiveDrumEngine(audioCtx,drumBus);
  for(const [v,n] of Object.entries(devMixerValues))liveDrumEngine.setUserGain(v,n);
  refreshDevMixerHud();
  return audioCtx;
}
async function preloadDrumSamples(){
  try{
    ensureAudioEngine();
    setPreload("drums",0,{label:"この曲で使うドラム音を準備中"});
    const items=(chart?.notes||[]).map(n=>{
      const mapped=applyDrumVoice(n,n.part);
      return {part:mapped.part,note:mapped.note,velocity:humanizedVelocity(n.velocity)};
    });
    drumPreloadPromise=liveDrumEngine.preloadForNotes(items,p=>setPreload("drums",p.ratio,{label:"この曲で使うドラム音を読み込み中",failed:(p.failures?.length||0)>0&&p.ratio>=1}));
    await drumPreloadPromise;
    if(liveDrumEngine.preloadFailures?.length)throw new Error("ドラム音 "+liveDrumEngine.preloadFailures.length+"件の読み込みに失敗");
    setPreload("drums",1,{label:"この曲で使うドラム音の読み込み完了"});
  }catch(err){
    setPreload("drums",1,{label:"ドラム音の読み込み失敗",failed:true});
    setStatus("ドラム音の事前読み込みに失敗しました: "+err.message);
    throw err;
  }
}
async function ensureAudio(){
  ensureAudioEngine();
  if(!liveDrumEngine.ready){
    drumPreloadPromise??=preloadDrumSamples();
    await drumPreloadPromise;
  }
  if(audioCtx.state==="suspended")await audioCtx.resume();
  return audioCtx;
}
function trackNode(node){scheduledNodes.push(node);node.addEventListener?.("ended",()=>{scheduledNodes=scheduledNodes.filter(x=>x!==node)},{once:true})}
function stopScheduled(){for(const n of scheduledNodes){try{n.stop()}catch{}}scheduledNodes=[];liveDrumEngine?.stop()}
function noiseBuffer(seconds=.25){const len=Math.max(1,Math.round(audioCtx.sampleRate*seconds)),b=audioCtx.createBuffer(1,len,audioCtx.sampleRate),d=b.getChannelData(0);let prev=0;for(let i=0;i<len;i++){const white=Math.random()*2-1;prev=prev*.72+white*.28;d[i]=white*.72+prev*.28}return b}
function gainEnv(t,peak,attack,decay,target=null){const g=audioCtx.createGain();g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(Math.max(.0002,peak),t+attack);g.gain.exponentialRampToValueAtTime(.0001,t+decay);g.connect(target||drumBus||audioCtx.destination);return g}
function tone(freq,t,dur,gain,type="sine",endFreq=null,attack=.002,target=null,detune=0){const o=audioCtx.createOscillator(),g=gainEnv(t,gain,attack,dur,target);o.type=type;o.frequency.setValueAtTime(freq,t);o.detune.value=detune;if(endFreq)o.frequency.exponentialRampToValueAtTime(Math.max(20,endFreq),t+dur*.72);o.connect(g);o.start(t);o.stop(t+dur+.025);trackNode(o)}
function filteredNoise(t,dur,gain,type,freq,q=.7,attack=.001,target=null){const s=audioCtx.createBufferSource(),f=audioCtx.createBiquadFilter(),g=gainEnv(t,gain,attack,dur,target);s.buffer=noiseBuffer(dur+.04);f.type=type;f.frequency.value=freq;f.Q.value=q;s.connect(f);f.connect(g);s.start(t);s.stop(t+dur+.04);trackNode(s)}
function metalPartials(t,dur,gain,freqs,target=null){for(const [i,f] of freqs.entries())tone(f,t+i*.0007,dur*(1-i*.055),gain/(1+i*.38),i%2?"sine":"triangle",f*(.82+i*.018),.001,target,(Math.random()-.5)*10)}
const DRUM_ROOM={};
function ensureDrumRoom(){if(DRUM_ROOM.close)return DRUM_ROOM;const input=audioCtx.createGain(),close=audioCtx.createGain(),room=audioCtx.createGain(),delayA=audioCtx.createDelay(.25),delayB=audioCtx.createDelay(.25),roomFilter=audioCtx.createBiquadFilter();close.gain.value=.82;room.gain.value=.24;delayA.delayTime.value=.017;delayB.delayTime.value=.043;roomFilter.type="lowpass";roomFilter.frequency.value=7600;input.connect(close);close.connect(drumBus);input.connect(delayA);input.connect(delayB);delayA.connect(roomFilter);delayB.connect(roomFilter);roomFilter.connect(room);room.connect(drumBus);Object.assign(DRUM_ROOM,{input,close,room});return DRUM_ROOM}
function humanizedVelocity(v){const n=Number(v);const x=Number.isFinite(n)?(n>1?n/127:n):.8;return Math.max(.78,Math.min(.88,.83+(x-.5)*.10))}
function drumAt(part,vel=.8,when=null,note=null){
  if(!$("drumSound").checked||!audioCtx||!liveDrumEngine)return;
  const t=Math.max(audioCtx.currentTime+.002,when??audioCtx.currentTime+.002);
  const mapped=applyDrumVoice(note||{},part);
  liveDrumEngine.trigger(mapped.part,vel,t,mapped.note);
  setTimeout(()=>flash(part),Math.max(0,(t-audioCtx.currentTime)*1000));
}
function stopOriginal(){if(originalSource){try{originalSource.stop()}catch{}originalSource=null}}
function startOriginal(){stopOriginal();if(!audioBuffer||!$("originalSound").checked||!audioCtx)return;const offset=Math.max(0,Math.min(playAnchorChart,audioBuffer.duration-.001));if(offset>=audioBuffer.duration)return;originalSource=audioCtx.createBufferSource();originalSource.buffer=audioBuffer;originalSource.playbackRate.value=playSpeed;originalSource.connect(audioCtx.destination);originalSource.start(playAnchorCtx,offset)}
function chartTimeFromClock(){if(!playing)return clampTime(time);const elapsed=Math.max(0,(performance.now()-playAnchorPerf)/1000);return clampTime(playAnchorChart+elapsed*playSpeed)}
function resetNextNote(at=time){const t=clampTime(at);nextNote=chart.notes.findIndex(n=>n.time>=t-.005);if(nextNote<0)nextNote=chart.notes.length}
function resetMetronome(at=time){const beatSec=60/(chart.bpm||120);nextMetronomeBeat=Math.max(0,Math.ceil((clampTime(at)-.005)/beatSec))}
function metronomeAt(beatIndex,when){if(!$("metronomeSound")?.checked||!audioCtx)return;const accent=beatIndex%4===0;tone(accent?1760:1180,when,.045,accent?.11:.07,"square",accent?1500:1000)}
function scheduleMetronome(horizon){if(!$("metronomeSound")?.checked||!audioCtx)return;const beatSec=60/(chart.bpm||120);while(true){const beatTime=nextMetronomeBeat*beatSec,target=playAnchorCtx+(beatTime-playAnchorChart)/playSpeed;if(target>horizon)break;if(target>=audioCtx.currentTime-.03)metronomeAt(nextMetronomeBeat,target);nextMetronomeBeat++}}
function scheduleAhead(){if(!playing||!audioCtx)return;const horizon=audioCtx.currentTime+.12;while(nextNote<chart.notes.length){const n=chart.notes[nextNote],target=playAnchorCtx+(n.time-playAnchorChart)/playSpeed;if(target>horizon)break;if(target>=audioCtx.currentTime-.03)drumAt(n.part,humanizedVelocity(n.velocity),target,n);nextNote++}scheduleMetronome(horizon)}
async function startPlayback(){
  if(playing)return;
  if(!startupReady){renderPreload();setStatus("読み込みが100%になるまでお待ちください。");return;}
  if(time>=chart.duration)time=0;
  time=clampTime(time);
  playSpeed=currentSpeed();
  playAnchorChart=time;
  playAnchorPerf=performance.now();
  playing=true;
  resetNextNote(playAnchorChart);
  resetMetronome(playAnchorChart);
  $("playPause").textContent="一時停止 ❚❚";
  setStatus("再生中");
  try{
    await ensureAudio();
    if(!playing)return;
    const elapsed=Math.max(0,(performance.now()-playAnchorPerf)/1000);
    playAnchorCtx=audioCtx.currentTime+.05;
    playAnchorChart=clampTime(playAnchorChart+elapsed*playSpeed);
    playAnchorPerf=performance.now()+50;
    resetNextNote(playAnchorChart);
    resetMetronome(playAnchorChart);
    startOriginal();
    scheduleAhead();
    schedulerTimer=setInterval(scheduleAhead,20);
  }catch(err){
    setStatus("譜面は再生中です。端末の音声初期化に失敗したためドラム音のみ鳴らせません: "+err.message);
  }
}
function pausePlayback(update=true){if(update&&playing)time=chartTimeFromClock();playing=false;if(schedulerTimer){clearInterval(schedulerTimer);schedulerTimer=null}stopOriginal();stopScheduled();if(startupReady)$("playPause").textContent="再生 ▶";else renderPreload();updateTime();draw()}
function toggle(){if(!startupReady&&!playing){renderPreload();return}playing?pausePlayback():startPlayback()}
function seek(v){const was=playing;if(was)pausePlayback();time=clampTime(v);resetNextNote(time);resetMetronome(time);updateTime();draw();if(was)startPlayback()}
function restartPlaybackAtClock(){if(!playing)return;const t=chartTimeFromClock();pausePlayback(false);time=clampTime(t);startPlayback()}
function loop(){if(playing){time=chartTimeFromClock();if(time>=chart.duration){pausePlayback(false);time=chart.duration;updateTime();draw()}else{updateTime();draw()}}updateCharacterPrototype(time,chart?.name||"",playing?playSpeed:currentSpeed(),playing);requestAnimationFrame(loop)}

$("chartFile").addEventListener("change",async e=>{const f=e.target.files?.[0];if(!f)return;try{setPreload("chart",0,{label:"譜面を解析中"});setStatus("譜面を解析しています…");setChart(await parseChart(f));setPreload("chart",1,{label:"譜面の読み込み完了"});drumPreloadPromise=null;preloadDrumSamples().catch(()=>{});setStatus(`${f.name} を読み込みました。`)}catch(err){setPreload("chart",1,{label:"譜面の読み込み失敗",failed:true});setStatus(err.message)}});
$("audioFile").addEventListener("change",async e=>{const f=e.target.files?.[0];if(!f)return;try{pausePlayback();setStatus("元音源を解析しています…");audioBuffer=await decodeAudio(f);onsets=analyzeOnsets(audioBuffer,chart.bpm);$("alignAudio").disabled=false;setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。同じWeb Audio時計で同期再生します。`)}catch(err){setStatus("元音源の読み込みに失敗しました: "+err.message)}});
$("alignAudio").onclick=()=>{const was=playing,t=was?chartTimeFromClock():time;if(was)pausePlayback(false);const r=realignNotes(chart.notes,onsets,chart.bpm);chart={...chart,notes:r.notes};setDrumGlowNotes(chart.notes);time=clampTime(t);resetNextNote(time);draw();if(was)startPlayback();setStatus(`音源同期補正: ${r.stats.moved}ノーツを補正、平均移動 ${r.stats.meanShiftMs.toFixed(1)}ms。`)};
$("loadSample").onclick=()=>{setChart(makeSample());setStatus("サンプルを読み込みました。")};
async function loadFinalChart({label,path,fileName,status}){setPreload("chart",0,{label:"譜面を読み込み中"});try{setStatus(label+" 完成譜面を読み込んでいます…");const controller=new AbortController();const timeout=setTimeout(()=>controller.abort("chart_timeout"),20000);let res;try{res=await fetch(path,{cache:"no-store",signal:controller.signal})}finally{clearTimeout(timeout)}if(!res.ok)throw new Error("完成譜面を取得できませんでした (HTTP "+res.status+")");const data=await res.json(),file=new File([JSON.stringify(data)],fileName,{type:"application/json"});window.dispatchEvent(new CustomEvent("dtx-chart-change",{detail:{name:data.name||label}}));setChart(await parseChart(file));setPreload("chart",1,{label:"譜面の読み込み完了"});drumPreloadPromise=null;preloadDrumSamples().catch(()=>{});setStatus(status)}catch(err){setPreload("chart",1,{label:"譜面の読み込み失敗",failed:true});setStatus(label+" 完成譜面の読み込みに失敗しました: "+err.message)}}
const SONGS={
  luna:{label:"Luna say maybe",path:"./charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json",fileName:"Luna_say_maybe_FINAL_notes.json",status:"Luna say maybe 完成譜面（Songsterr基準・元音源+1.693秒同期）を読み込みました。リアルドラム音色（2番Aメロのサイドスティック含む）で再生できます。"},
  kanaetai:{label:"叶えたい、ことばかり",path:"./charts/kanaetai_koto_bakari/Kanaetai_koto_bakari_FINAL_notes.json",fileName:"Kanaetai_koto_bakari_FINAL_notes.json",status:"叶えたい、ことばかり FINAL譜面（Songsterr s2808958 rev 3694097 Drums・全144小節）を読み込みました。原曲音源との最終ミリ秒同期のみ未実施です。"},
  ittai:{label:"一体いつから",path:"./charts/ittai_itsukara/Ittai_itsukara_FINAL_notes.json",fileName:"Ittai_itsukara_FINAL_notes.json",status:"一体いつから FINAL譜面（Songsterr s3705140 rev 4853202 Drums・全181小節・175 BPM）を読み込みました。原曲音源との最終ミリ秒同期のみ未実施です。"}
};
// The third-party Watagashi MIDI is licensed for personal use only.
// Keep the imported original exclusively in this browser's IndexedDB; never publish it.
const WATAGASHI_NAME="わたがし / back number";
let watagashiLoadSerial=0;
function openWatagashiDB(){
 return new Promise((resolve,reject)=>{
  const request=indexedDB.open("dtx-watagashi-local-midi",1);
  request.onupgradeneeded=()=>request.result.createObjectStore("charts");
  request.onsuccess=()=>resolve(request.result);
  request.onerror=()=>reject(request.error||new Error("端末の譜面保存を開けません"));
 });
}
async function readSavedWatagashiMidi(){
 const db=await openWatagashiDB();
 try{
  return await new Promise((resolve,reject)=>{
   const request=db.transaction("charts","readonly").objectStore("charts").get("watagashi");
   request.onsuccess=()=>resolve(request.result||null);
   request.onerror=()=>reject(request.error);
  });
 }finally{db.close()}
}
async function saveWatagashiMidi(file){
 const db=await openWatagashiDB();
 try{
  await new Promise((resolve,reject)=>{
   const tx=db.transaction("charts","readwrite");
   tx.objectStore("charts").put(file,"watagashi");
   tx.oncomplete=()=>resolve();
   tx.onerror=()=>reject(tx.error);
  });
 }finally{db.close()}
}
async function installWatagashiMidi(file,{store=false,serial=watagashiLoadSerial}={}){
 try{
  if($("songSelect").value!=="watagashi"||serial!==watagashiLoadSerial)return;
  setStatus("わたがしのMIDIからドラムパートを抽出しています…");
  const midi=file instanceof File?file:new File([file],"watagashi.mid",{type:"audio/midi"});
  const parsed=await parseChart(midi);
  if(!parsed.notes?.length)throw new Error("ドラムのノーツが見つかりません。チャンネル10にドラムがあるMIDIが必要です。");
  if($("songSelect").value!=="watagashi"||serial!==watagashiLoadSerial)return;
  const normalized={...parsed,name:WATAGASHI_NAME,artist:"back number",source:"端末内MIDI（個人利用専用）",alignment:{pendingOriginalAudioSync:true},notes:parsed.notes};
  setChart(normalized);
  chartNeedsImport=false;
  setPreload("chart",1,{label:"わたがしのMIDI読込完了"});
  if(store)try{await saveWatagashiMidi(midi)}catch(error){console.warn("MIDI local save failed",error);setStatus("譜面は読み込めましたが端末内への保存に失敗しました: "+error.message)}
  drumPreloadPromise=null;
  await preloadDrumSamples();
  if($("songSelect").value==="watagashi"&&serial===watagashiLoadSerial)setStatus("わたがし："+normalized.notes.length.toLocaleString()+"ドラムノーツを読み込みました。元音源との厳密な同期は未検証です。");
 }catch(error){
  if($("songSelect").value==="watagashi"&&serial===watagashiLoadSerial){
   chartNeedsImport=true;setPreload("chart",1,{label:"MIDI再選択が必要"});
   setStatus("わたがしのMIDI読込エラー: "+error.message);
  }
 }
}
async function loadWatagashi(){
 const serial=++watagashiLoadSerial;
 chartNeedsImport=true;
 setChart({name:WATAGASHI_NAME+"（譜面未登録）",bpm:124,duration:260,notes:[]});
 setPreload("chart",1,{label:"端末のMIDIを確認中"});
 renderPreload();
 window.dispatchEvent(new CustomEvent("dtx-chart-change",{detail:{name:WATAGASHI_NAME}}));
 setStatus("わたがし：端末に保存済みのMIDIを確認しています。未登録なら上の「MIDIファイルを選択」から読み込んでください。");
 try{
  const saved=await readSavedWatagashiMidi();
  if(serial!==watagashiLoadSerial||$("songSelect").value!=="watagashi")return;
  if(saved)await installWatagashiMidi(saved,{serial});
  else setStatus("わたがし：ドラムMIDIがまだ登録されていません。配布ページから入手し、上のボタンで選択してください。");
 }catch(error){
  if(serial===watagashiLoadSerial&&$("songSelect").value==="watagashi")
   setStatus("わたがし：保存済み譜面を読めませんでした。MIDIファイルを選択してください。"+error.message);
 }
}
function loadSelectedSong(){
 const key=$("songSelect").value;
 $("watagashiPanel").hidden=key!=="watagashi";
 if(key==="watagashi")return loadWatagashi();
 ++watagashiLoadSerial;chartNeedsImport=false;
 renderPreload();
 return loadFinalChart(SONGS[key]||SONGS.luna);
}
$("watagashiMidiFile").addEventListener("change",async event=>{
 const f=event.target.files?.[0];
 if(!f)return;
 const serial=watagashiLoadSerial;
 await installWatagashiMidi(f,{store:true,serial});
 event.target.value="";
});
$("songSelect").addEventListener("change",loadSelectedSong);
$("exportJson").onclick=()=>{const safe=(chart.name||"dtx-drum-flow").replace(/[\\/:*?"<>|]+/g,"_");downloadText(`${safe}.json`,JSON.stringify(chartToJson(),null,2));setStatus("現在の譜面をJSONで保存しました。")};
$("playPause").onclick=toggle;$("rewind5").onclick=()=>seek(chartTimeFromClock()-5);$("forward5").onclick=()=>seek(chartTimeFromClock()+5);$("rewindMeasure").onclick=()=>seek(chartTimeFromClock()-measureSeconds()*4);$("forwardMeasure").onclick=()=>seek(chartTimeFromClock()+measureSeconds()*4);$("timeline").oninput=e=>seek(Number(e.target.value));$("speed").onchange=restartPlaybackAtClock;
function syncSoundToggleUi(){$("drumSoundState").textContent=$("drumSound").checked?"ON":"OFF";$("metronomeSoundState").textContent=$("metronomeSound").checked?"ON":"OFF";$("originalSoundState").textContent=$("originalSound").checked?"ON":"OFF"}
$("drumSound").onchange=()=>{syncSoundToggleUi();if(playing)restartPlaybackAtClock()};$("metronomeSound").onchange=()=>{syncSoundToggleUi();resetMetronome(chartTimeFromClock());if(playing&&audioCtx)scheduleAhead()};$("originalSound").onchange=()=>{syncSoundToggleUi();if(playing)restartPlaybackAtClock()};
$("noteSpeed").oninput=e=>{noteSpeed=Math.max(.5,Math.min(8,Number(e.target.value)||1));$("noteSpeedValue").textContent=noteSpeed.toFixed(1)+"×";draw()};
// Two taps on the LEFT chart surface; keep the second finger down and drag
// horizontally to scrub the timeline. No playback restart until finger release.
const leftSeekZone=document.querySelector(".seek-zone.left");
const rightSeekZone=document.querySelector(".seek-zone.right");
const scrubGesture={firstTapAt:0,firstX:0,firstY:0,down:null,active:false,wasPlaying:false,startTime:0};
const DOUBLE_TAP_MS=420,DOUBLE_TAP_RADIUS=44,SCRUB_ACTIVATION_PX=7;
function scrubPreview(t){
 time=clampTime(t);resetNextNote(time);resetMetronome(time);updateTime();draw();
 updateCharacterPrototype(time,chart?.name||"",currentSpeed(),false);
}
leftSeekZone.addEventListener("pointerdown",e=>{
 if(e.pointerType==="mouse"&&e.button!==0)return;
 if(scrubGesture.down)return;
 const now=performance.now();
 const near=Math.hypot(e.clientX-scrubGesture.firstX,e.clientY-scrubGesture.firstY)<=DOUBLE_TAP_RADIUS;
 const second=now-scrubGesture.firstTapAt<=DOUBLE_TAP_MS&&near;
 scrubGesture.down={id:e.pointerId,x:e.clientX,y:e.clientY,second,moved:false};
 scrubGesture.firstTapAt=0;
 if(second){
   scrubGesture.startTime=chartTimeFromClock();
   scrubGesture.wasPlaying=playing;
   // Capture the pointer so dragging beyond the left half still works.
   leftSeekZone.setPointerCapture?.(e.pointerId);
 }
});
leftSeekZone.addEventListener("pointermove",e=>{
 const d=scrubGesture.down;
 if(!d||d.id!==e.pointerId)return;
 const dx=e.clientX-d.x,dy=e.clientY-d.y;
 if(Math.hypot(dx,dy)>DOUBLE_TAP_RADIUS)d.moved=true;
 if(!d.second)return;
 if(!scrubGesture.active){
   if(Math.abs(dx)<SCRUB_ACTIVATION_PX||Math.abs(dx)<Math.abs(dy)*1.15)return;
   scrubGesture.active=true;
   if(scrubGesture.wasPlaying)pausePlayback(false);
   leftSeekZone.classList.add("scrubbing");
 }
 if(e.cancelable)e.preventDefault();
 // Full chart width corresponds to four measures; right = forward, left = backward.
 const width=Math.max(1,canvas.getBoundingClientRect().width);
 scrubPreview(scrubGesture.startTime+dx/width*measureSeconds()*4);
});
function finishScrubGesture(e,cancelled=false){
 const d=scrubGesture.down;
 if(!d||d.id!==e.pointerId)return;
 if(scrubGesture.active){
   if(e.cancelable)e.preventDefault();
   const dx=e.clientX-d.x;
   if(!cancelled) {
     const width=Math.max(1,canvas.getBoundingClientRect().width);
     scrubPreview(scrubGesture.startTime+dx/width*measureSeconds()*4);
   }
   leftSeekZone.classList.remove("scrubbing");
   scrubGesture.active=false;
   scrubGesture.firstTapAt=0;
   if(scrubGesture.wasPlaying)startPlayback();
 }else if(!cancelled){
   if(d.second){
     // A double tap without dragging keeps the previous four-measure rewind.
     seek(chartTimeFromClock()-measureSeconds()*4);
   }else if(!d.moved){
     scrubGesture.firstTapAt=performance.now();
     scrubGesture.firstX=e.clientX;
     scrubGesture.firstY=e.clientY;
   }
 }
 scrubGesture.down=null;
 if(leftSeekZone.hasPointerCapture?.(e.pointerId))leftSeekZone.releasePointerCapture(e.pointerId);
}
leftSeekZone.addEventListener("pointerup",e=>finishScrubGesture(e));
leftSeekZone.addEventListener("pointercancel",e=>finishScrubGesture(e,true));
leftSeekZone.addEventListener("lostpointercapture",e=>{if(scrubGesture.down?.id===e.pointerId)finishScrubGesture(e,true)});
let rightDoubleTapAt=0;
rightSeekZone.addEventListener("pointerup",()=>{
 const now=performance.now();
 if(now-rightDoubleTapAt<350){seek(chartTimeFromClock()+measureSeconds()*4);rightDoubleTapAt=0}
 else rightDoubleTapAt=now;
});
function measureSeconds(){return 240/(chart.bpm||120)}
addEventListener("keydown",e=>{if(e.target.matches("input,select"))return;if(e.code==="Space"){e.preventDefault();toggle()}if(e.code==="ArrowLeft")seek(chartTimeFromClock()-5);if(e.code==="ArrowRight")seek(chartTimeFromClock()+5)});
const dropZone=$("dropZone");for(const ev of ["dragenter","dragover"]){dropZone.addEventListener(ev,e=>{e.preventDefault();dropZone.classList.add("dragover")})}for(const ev of ["dragleave","drop"]){dropZone.addEventListener(ev,e=>{e.preventDefault();dropZone.classList.remove("dragover")})}
dropZone.addEventListener("drop",async e=>{const files=[...(e.dataTransfer?.files||[])];for(const f of files){const ext=f.name.split(".").pop().toLowerCase();try{if(["mid","midi","dtx","gda","json"].includes(ext)){setStatus("譜面を解析しています…");setChart(await parseChart(f));setStatus(`${f.name} を読み込みました。`)}else if(f.type.startsWith("audio/")){pausePlayback();setStatus("元音源を解析しています…");audioBuffer=await decodeAudio(f);onsets=analyzeOnsets(audioBuffer,chart.bpm);$("alignAudio").disabled=false;setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。`)}}catch(err){setStatus(`${f.name}: ${err.message}`)}}});
initDevAudioMixer();window.__DTX_APP_READY__=true;addEventListener("resize",resize);makeParts();syncSoundToggleUi();setChart(chart);resize();renderPreload();initCharacterPrototype().catch(err=>{console.error("Drum illustration initialization failed",err);setPreload("character",1,{label:"ドラム画像エラー",failed:true});setStatus("ドラム画像の初期化エラー: "+err.message)});requestAnimationFrame(loop);loadSelectedSong();setTimeout(()=>{if(!startupReady){const missing=Object.entries(preloadState).filter(([,v])=>v.ratio<1||v.failed).map(([name,v])=>name+" "+Math.round(v.ratio*100)+"%"+(v.failed?" ERROR":"")).join(" / ");if(missing)setStatus("読み込み未完了: "+missing+"。通信・画像のエラーを確認してください。")}},15000);
