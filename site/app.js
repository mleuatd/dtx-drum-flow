import {makeSample,parseChart} from "./parsers.js";
import {decodeAudio,analyzeOnsets,realignNotes} from "./audio-analysis.js";
import {LiveDrumEngine} from "./live-drum-engine.js?v=20260919-acoustic-r20";
import {applyDrumVoice} from "./drum-note-sound-map.js?v=20260919-acoustic-r20";
import {initCharacterPrototype,updateCharacterPrototype} from "./character-prototype.js?v=20260919-public-runtime-qa-r1";

const PARTS=["LB","LC","HH","LP","SN","BD","HT","LT","FT","RD","RC"];
const PART_LABEL={LC:"左シンバル",HH:"ハイハット",SN:"スネア",HT:"ハイタム",LT:"ロータム",FT:"フロアタム",RC:"右シンバル",RD:"ライド",LP:"左足HH",LB:"左足BD",BD:"バスドラム"};
const PART_ICON={LC:"◯",HH:"◎",SN:"🥁",HT:"◒",LT:"◓",FT:"◉",RC:"◯",RD:"◌",LP:"⌁",LB:"●",BD:"⬤"};
const $=id=>document.getElementById(id),canvas=$("laneCanvas"),ctx=canvas.getContext("2d");
let chart=makeSample(),time=0,playing=false,audioBuffer=null,onsets=[],audioCtx=null,drumBus=null,liveDrumEngine=null,originalSource=null,schedulerTimer=null,scheduledNodes=[],nextNote=0,nextMetronomeBeat=0,playAnchorCtx=0,playAnchorPerf=0,playAnchorChart=0,playSpeed=1,noteSpeed=1;
const partEls=new Map();
const DEV_MIXER=[
 ["kick","BD/LB"],["snare","SN"],["sideStick","SideStick"],["hihatClosed","HH Closed"],["hihatOpen","HH Open"],["hihatPedal","LP HH"],
 ["tomHigh","HT"],["tomLow","LT"],["tomFloor","FT"],["ride","RD"],["rideBell","Ride Bell"],["crashLeft","LC"],["crashRight","RC"]
];
const DEV_MIXER_DEFAULT={kick:2.5,snare:1,sideStick:.2,hihatClosed:.2,hihatOpen:.2,hihatPedal:1,tomHigh:1,tomLow:1,tomFloor:1.05,ride:.2,rideBell:.25,crashLeft:.2,crashRight:.2};
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
function setChart(c){pausePlayback(false);chart=c;time=0;nextNote=0;document.querySelector(".stage")?.classList.toggle("luna-stage",String(c?.name||"").toLowerCase().includes("luna"));$("timeline").max=c.duration;$("duration").textContent=fmt(c.duration);$("chartName").textContent=c.name;$("chartMeta").textContent=`${Math.round(c.bpm)} BPM · ${c.duration.toFixed(1)}秒 · ${c.notes.length.toLocaleString()}ノーツ`;const name=c.name||"";let stage="LUNA / DRUM CHART",badge="LUNA FINAL";if(name.includes("叶えたい")){stage="叶えたい、ことばかり / DRUM CHART";badge="KANAETAI FINAL"}else if(name.includes("一体いつから")){stage="一体いつから / DRUM CHART";badge="ITTAI FINAL"}if($("stageTitle"))$("stageTitle").textContent=stage;if($("chartBadge"))$("chartBadge").textContent=badge;draw();updateTime()}
function updateTime(){$("currentTime").textContent=fmt(time);const mirror=$("currentTimeMirror");if(mirror)mirror.textContent=fmt(time);$("timeline").value=time}
function resize(){const r=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw()}
function draw(){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const lane=w/PARTS.length,isLuna=String(chart?.name||"").toLowerCase().includes("luna");if(!isLuna){ctx.fillStyle="#0e172a";ctx.fillRect(0,0,w,h)}ctx.strokeStyle=isLuna?"rgba(34,54,86,.62)":"#223656";ctx.lineWidth=1;for(let i=1;i<PARTS.length;i++){ctx.beginPath();ctx.moveTo(i*lane,0);ctx.lineTo(i*lane,h);ctx.stroke()}const judgeY=h-36,lookAhead=3.3/noteSpeed;const hitNow=chart.notes.some(n=>Math.abs(n.time-time)<=Math.max(.025,.04/currentSpeed()));ctx.save();ctx.strokeStyle=hitNow?"#ffffff":"#86a7ff";ctx.shadowColor=hitNow?"#9fc5ff":"transparent";ctx.shadowBlur=hitNow?22:0;ctx.lineWidth=hitNow?5:3;ctx.beginPath();ctx.moveTo(0,judgeY);ctx.lineTo(w,judgeY);ctx.stroke();ctx.restore();for(const n of chart.notes){const dt=n.time-time;if(dt<0||dt>lookAhead)continue;const x=(PARTS.indexOf(n.part)+.5)*lane,y=judgeY-(dt/lookAhead)*(judgeY-20),conf=Number(n.alignConfidence||0),radius=Math.max(5,lane*.12)*(conf>0?(.78+.22*conf):1);ctx.globalAlpha=conf>0?Math.max(.35,conf):1;ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.fillStyle=conf>0?(conf>=.65?"#8ad8ff":conf>=.35?"#f0d889":"#e59696"):"#f2f5ff";ctx.fill();ctx.globalAlpha=1}}
function makeParts(){const root=$("parts");root.innerHTML="";for(const p of PARTS){const el=document.createElement("div");el.className="part";el.innerHTML=`<span class="icon" aria-hidden="true">${PART_ICON[p]}</span><strong>${p}</strong><span class="label">${PART_LABEL[p]}</span>`;root.append(el);partEls.set(p,el)}}
function flash(part){const el=partEls.get(part);if(!el)return;el.classList.add("hit");setTimeout(()=>el.classList.remove("hit"),90)}
async function ensureAudio(){
  audioCtx??=new (window.AudioContext||window.webkitAudioContext)({latencyHint:"interactive"});
  if(!drumBus){
    const input=audioCtx.createGain(),comp=audioCtx.createDynamicsCompressor(),out=audioCtx.createGain();
    input.gain.value=1;
    comp.threshold.value=-4;comp.knee.value=12;comp.ratio.value=1.35;comp.attack.value=.01;comp.release.value=.055;
    out.gain.value=1;input.connect(comp);comp.connect(out);out.connect(audioCtx.destination);drumBus=input;
  }
  liveDrumEngine??=new LiveDrumEngine(audioCtx,drumBus);for(const [v,n] of Object.entries(devMixerValues))liveDrumEngine.setUserGain(v,n);refreshDevMixerHud();
  if(!liveDrumEngine.ready)liveDrumEngine.preload().catch(err=>console.warn("Acoustic drum preload failed",err));
  if(audioCtx.state==="suspended")await audioCtx.resume();
  return audioCtx
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
function pausePlayback(update=true){if(update&&playing)time=chartTimeFromClock();playing=false;if(schedulerTimer){clearInterval(schedulerTimer);schedulerTimer=null}stopOriginal();stopScheduled();$("playPause").textContent="再生 ▶";updateTime();draw()}
function toggle(){playing?pausePlayback():startPlayback()}
function seek(v){const was=playing;if(was)pausePlayback();time=clampTime(v);resetNextNote(time);resetMetronome(time);updateTime();draw();if(was)startPlayback()}
function restartPlaybackAtClock(){if(!playing)return;const t=chartTimeFromClock();pausePlayback(false);time=clampTime(t);startPlayback()}
function loop(){if(playing){time=chartTimeFromClock();if(time>=chart.duration){pausePlayback(false);time=chart.duration;updateTime();draw()}else{updateTime();draw()}}updateCharacterPrototype(time,chart?.name||"");requestAnimationFrame(loop)}

$("chartFile").addEventListener("change",async e=>{const f=e.target.files?.[0];if(!f)return;try{setStatus("譜面を解析しています…");setChart(await parseChart(f));setStatus(`${f.name} を読み込みました。`)}catch(err){setStatus(err.message)}});
$("audioFile").addEventListener("change",async e=>{const f=e.target.files?.[0];if(!f)return;try{pausePlayback();setStatus("元音源を解析しています…");audioBuffer=await decodeAudio(f);onsets=analyzeOnsets(audioBuffer,chart.bpm);$("alignAudio").disabled=false;setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。同じWeb Audio時計で同期再生します。`)}catch(err){setStatus("元音源の読み込みに失敗しました: "+err.message)}});
$("alignAudio").onclick=()=>{const was=playing,t=was?chartTimeFromClock():time;if(was)pausePlayback(false);const r=realignNotes(chart.notes,onsets,chart.bpm);chart={...chart,notes:r.notes};time=clampTime(t);resetNextNote(time);draw();if(was)startPlayback();setStatus(`音源同期補正: ${r.stats.moved}ノーツを補正、平均移動 ${r.stats.meanShiftMs.toFixed(1)}ms。`)};
$("loadSample").onclick=()=>{setChart(makeSample());setStatus("サンプルを読み込みました。")};
async function loadFinalChart({label,path,fileName,status}){try{setStatus(label+" 完成譜面を読み込んでいます…");const res=await fetch(path,{cache:"no-store"});if(!res.ok)throw new Error("完成譜面を取得できませんでした (HTTP "+res.status+")");const data=await res.json(),file=new File([JSON.stringify(data)],fileName,{type:"application/json"});window.dispatchEvent(new CustomEvent("dtx-chart-change",{detail:{name:data.name||label}}));setChart(await parseChart(file));setStatus(status)}catch(err){setStatus(label+" 完成譜面の読み込みに失敗しました: "+err.message)}}
const SONGS={
  luna:{label:"Luna say maybe",path:"./charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json",fileName:"Luna_say_maybe_FINAL_notes.json",status:"Luna say maybe 完成譜面（Songsterr基準・元音源+1.693秒同期）を読み込みました。リアルドラム音色（2番Aメロのサイドスティック含む）で再生できます。"},
  kanaetai:{label:"叶えたい、ことばかり",path:"./charts/kanaetai_koto_bakari/Kanaetai_koto_bakari_FINAL_notes.json",fileName:"Kanaetai_koto_bakari_FINAL_notes.json",status:"叶えたい、ことばかり FINAL譜面（Songsterr s2808958 rev 3694097 Drums・全144小節）を読み込みました。原曲音源との最終ミリ秒同期のみ未実施です。"},
  ittai:{label:"一体いつから",path:"./charts/ittai_itsukara/Ittai_itsukara_FINAL_notes.json",fileName:"Ittai_itsukara_FINAL_notes.json",status:"一体いつから FINAL譜面（Songsterr s3705140 rev 4853202 Drums・全181小節・175 BPM）を読み込みました。原曲音源との最終ミリ秒同期のみ未実施です。"}
};
function loadSelectedSong(){const cfg=SONGS[$("songSelect").value]||SONGS.luna;return loadFinalChart(cfg)}
$("songSelect").addEventListener("change",loadSelectedSong);
$("exportJson").onclick=()=>{const safe=(chart.name||"dtx-drum-flow").replace(/[\\/:*?"<>|]+/g,"_");downloadText(`${safe}.json`,JSON.stringify(chartToJson(),null,2));setStatus("現在の譜面をJSONで保存しました。")};
$("playPause").onclick=toggle;$("rewind5").onclick=()=>seek(chartTimeFromClock()-5);$("forward5").onclick=()=>seek(chartTimeFromClock()+5);$("rewindMeasure").onclick=()=>seek(chartTimeFromClock()-measureSeconds()*4);$("forwardMeasure").onclick=()=>seek(chartTimeFromClock()+measureSeconds()*4);$("timeline").oninput=e=>seek(Number(e.target.value));$("speed").onchange=restartPlaybackAtClock;
function syncSoundToggleUi(){$("drumSoundState").textContent=$("drumSound").checked?"ON":"OFF";$("metronomeSoundState").textContent=$("metronomeSound").checked?"ON":"OFF";$("originalSoundState").textContent=$("originalSound").checked?"ON":"OFF"}
$("drumSound").onchange=()=>{syncSoundToggleUi();if(playing)restartPlaybackAtClock()};$("metronomeSound").onchange=()=>{syncSoundToggleUi();resetMetronome(chartTimeFromClock());if(playing&&audioCtx)scheduleAhead()};$("originalSound").onchange=()=>{syncSoundToggleUi();if(playing)restartPlaybackAtClock()};
$("noteSpeed").oninput=e=>{noteSpeed=Math.max(.5,Math.min(8,Number(e.target.value)||1));$("noteSpeedValue").textContent=noteSpeed.toFixed(1)+"×";draw()};
for(const [sel,dir] of [[".seek-zone.left",-1],[".seek-zone.right",1]]){let last=0;document.querySelector(sel).addEventListener("pointerup",()=>{const now=performance.now();if(now-last<350)seek(chartTimeFromClock()+dir*measureSeconds()*4);last=now})}
function measureSeconds(){return 240/(chart.bpm||120)}
addEventListener("keydown",e=>{if(e.target.matches("input,select"))return;if(e.code==="Space"){e.preventDefault();toggle()}if(e.code==="ArrowLeft")seek(chartTimeFromClock()-5);if(e.code==="ArrowRight")seek(chartTimeFromClock()+5)});
const dropZone=$("dropZone");for(const ev of ["dragenter","dragover"]){dropZone.addEventListener(ev,e=>{e.preventDefault();dropZone.classList.add("dragover")})}for(const ev of ["dragleave","drop"]){dropZone.addEventListener(ev,e=>{e.preventDefault();dropZone.classList.remove("dragover")})}
dropZone.addEventListener("drop",async e=>{const files=[...(e.dataTransfer?.files||[])];for(const f of files){const ext=f.name.split(".").pop().toLowerCase();try{if(["mid","midi","dtx","gda","json"].includes(ext)){setStatus("譜面を解析しています…");setChart(await parseChart(f));setStatus(`${f.name} を読み込みました。`)}else if(f.type.startsWith("audio/")){pausePlayback();setStatus("元音源を解析しています…");audioBuffer=await decodeAudio(f);onsets=analyzeOnsets(audioBuffer,chart.bpm);$("alignAudio").disabled=false;setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。`)}}catch(err){setStatus(`${f.name}: ${err.message}`)}}});
initDevAudioMixer();window.__DTX_APP_READY__=true;addEventListener("resize",resize);makeParts();syncSoundToggleUi();setChart(chart);resize();initCharacterPrototype();requestAnimationFrame(loop);loadSelectedSong();
