import {makeSample,parseChart} from "./parsers.js";
import {decodeAudio,analyzeOnsets,realignNotes} from "./audio-analysis.js";

const PARTS=["LC","HH","SN","HT","LT","FT","RC","RD","LP","LB","BD"];
const PART_LABEL={LC:"左シンバル",HH:"ハイハット",SN:"スネア",HT:"ハイタム",LT:"ロータム",FT:"フロアタム",RC:"右シンバル",RD:"ライド",LP:"左足HH",LB:"左足BD",BD:"バスドラム"};
const PART_ICON={LC:"◯",HH:"◎",SN:"🥁",HT:"◒",LT:"◓",FT:"◉",RC:"◯",RD:"◌",LP:"⌁",LB:"●",BD:"⬤"};
const $=id=>document.getElementById(id),canvas=$("laneCanvas"),ctx=canvas.getContext("2d");

let chart=makeSample();
let time=0;
let playing=false;
let audioBuffer=null;
let onsets=[];
let audioCtx=null;
let originalSource=null;
let schedulerTimer=null;
let scheduledNodes=[];
let nextNote=0;
let playAnchorCtx=0;
let playAnchorChart=0;
let playSpeed=1;
let noteSpeed=1;
const partEls=new Map();

function fmt(s){s=Math.max(0,s);const m=Math.floor(s/60),sec=(s%60).toFixed(1).padStart(4,"0");return `${m}:${sec}`}
function setStatus(s){$("status").textContent=s}
function downloadText(name,text,type="application/json"){
  const blob=new Blob([text],{type});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");a.href=url;a.download=name;document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),500);
}
function chartToJson(){
  const partKind={BD:"kick",LB:"kick",SN:"snare",HH:"hihat",LP:"hihat",HT:"toms",LT:"toms",FT:"toms",LC:"cymbals",RC:"cymbals",RD:"cymbals"};
  return {
    bpm:chart.bpm,
    duration:chart.duration,
    name:chart.name,
    notes:chart.notes.map(n=>({
      time:Number(n.time.toFixed(6)),
      kind:partKind[n.part]||"unknown",
      part:n.part,
      velocity:Math.round(Math.max(0,Math.min(1,n.velocity??.8))*127),
      confidence:Number(n.alignConfidence||0)
    }))
  };
}
function currentSpeed(){return Number($("speed").value)||1}
function setChart(c){
  pausePlayback(false);
  chart=c;time=0;nextNote=0;
  $("timeline").max=c.duration;
  $("duration").textContent=fmt(c.duration);
  $("chartName").textContent=c.name;
  $("chartMeta").textContent=`${Math.round(c.bpm)} BPM · ${c.duration.toFixed(1)}秒 · ${c.notes.length}ノーツ`;
  draw();updateTime();
}
function updateTime(){
  $("currentTime").textContent=fmt(time);
  const mirror=$("currentTimeMirror");if(mirror)mirror.textContent=fmt(time);
  $("timeline").value=time
}
function resize(){const r=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw()}
function draw(){
  const w=canvas.clientWidth,h=canvas.clientHeight;
  ctx.clearRect(0,0,w,h);
  const lane=w/PARTS.length;
  ctx.fillStyle="#0e172a";ctx.fillRect(0,0,w,h);
  ctx.strokeStyle="#223656";ctx.lineWidth=1;
  for(let i=1;i<PARTS.length;i++){ctx.beginPath();ctx.moveTo(i*lane,0);ctx.lineTo(i*lane,h);ctx.stroke()}
  const judgeY=h-36;
  const lookAhead=3.3/noteSpeed;
  const hitNow=chart.notes.some(n=>Math.abs(n.time-time)<=Math.max(.025,.04/currentSpeed()));
  ctx.save();
  ctx.strokeStyle=hitNow?"#ffffff":"#86a7ff";
  ctx.shadowColor=hitNow?"#9fc5ff":"transparent";
  ctx.shadowBlur=hitNow?22:0;
  ctx.lineWidth=hitNow?5:3;
  ctx.beginPath();ctx.moveTo(0,judgeY);ctx.lineTo(w,judgeY);ctx.stroke();
  ctx.restore();
  for(const n of chart.notes){
    const dt=n.time-time;
    if(dt<0||dt>lookAhead)continue;
    const x=(PARTS.indexOf(n.part)+.5)*lane,y=judgeY-(dt/lookAhead)*(judgeY-20);
    const conf=Number(n.alignConfidence||0);
    const radius=Math.max(5,lane*.12)*(conf>0?(.78+.22*conf):1);
    ctx.globalAlpha=conf>0?Math.max(.35,conf):1;
    ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);
    ctx.fillStyle=conf>0?(conf>=.65?"#8ad8ff":conf>=.35?"#f0d889":"#e59696"):"#f2f5ff";ctx.fill();
    ctx.globalAlpha=1;
  }
}
function makeParts(){
  const root=$("parts");root.innerHTML="";
  for(const p of PARTS){
    const el=document.createElement("div");el.className="part";
    el.innerHTML=`<span class="icon" aria-hidden="true">${PART_ICON[p]}</span><strong>${p}</strong><span class="label">${PART_LABEL[p]}</span>`;
    root.append(el);partEls.set(p,el);
  }
}
function flash(part){
  const el=partEls.get(part);if(!el)return;
  el.classList.add("hit");setTimeout(()=>el.classList.remove("hit"),90);
}
function ensureAudio(){
  audioCtx??=new (window.AudioContext||window.webkitAudioContext)({latencyHint:"interactive"});
  if(audioCtx.state==="suspended")audioCtx.resume();
}
function trackNode(node){scheduledNodes.push(node);node.addEventListener?.("ended",()=>{scheduledNodes=scheduledNodes.filter(x=>x!==node)},{once:true})}
function stopScheduled(){
  for(const n of scheduledNodes){try{n.stop()}catch{}}
  scheduledNodes=[];
}
function drumAt(part,vel=.8,when=null){
  if(!$("drumSound").checked)return;
  ensureAudio();
  const t=Math.max(audioCtx.currentTime+.002,when??audioCtx.currentTime+.002);
  const g=audioCtx.createGain();
  g.gain.setValueAtTime(.0001,t);
  g.gain.exponentialRampToValueAtTime(.22*vel,t+.002);
  g.gain.exponentialRampToValueAtTime(.0001,t+.20);
  g.connect(audioCtx.destination);

  if(part==="BD"||part==="LB"){
    const o=audioCtx.createOscillator();
    o.frequency.setValueAtTime(125,t);o.frequency.exponentialRampToValueAtTime(48,t+.11);
    o.connect(g);o.start(t);o.stop(t+.22);trackNode(o);
  }else{
    const len=Math.round(audioCtx.sampleRate*.18),b=audioCtx.createBuffer(1,len,audioCtx.sampleRate),d=b.getChannelData(0);
    for(let i=0;i<len;i++)d[i]=(Math.random()*2-1)*(1-i/len);
    const s=audioCtx.createBufferSource();s.buffer=b;
    const f=audioCtx.createBiquadFilter();
    f.type=part==="HH"||part==="LC"||part==="RC"||part==="RD"?"highpass":"bandpass";
    f.frequency.value=part==="SN"?1800:part==="HH"?6500:part==="FT"?450:part==="LT"?700:part==="HT"?1050:3600;
    s.connect(f);f.connect(g);s.start(t);trackNode(s);
  }
  const visualDelay=Math.max(0,(t-audioCtx.currentTime)*1000);
  setTimeout(()=>flash(part),visualDelay);
}
function stopOriginal(){if(originalSource){try{originalSource.stop()}catch{} originalSource=null}}
function startOriginal(){
  stopOriginal();
  if(!audioBuffer||!$("originalSound").checked)return;
  const offset=Math.max(0,Math.min(time,audioBuffer.duration-.001));
  if(offset>=audioBuffer.duration)return;
  originalSource=audioCtx.createBufferSource();
  originalSource.buffer=audioBuffer;
  originalSource.playbackRate.value=playSpeed;
  originalSource.connect(audioCtx.destination);
  originalSource.start(playAnchorCtx,offset);
}
function chartTimeFromClock(){
  if(!playing||!audioCtx)return time;
  return playAnchorChart+(audioCtx.currentTime-playAnchorCtx)*playSpeed;
}
function resetNextNote(){
  nextNote=chart.notes.findIndex(n=>n.time>=time-.005);
  if(nextNote<0)nextNote=chart.notes.length;
}
function scheduleAhead(){
  if(!playing||!audioCtx)return;
  const horizon=audioCtx.currentTime+.10;
  while(nextNote<chart.notes.length){
    const n=chart.notes[nextNote];
    const target=playAnchorCtx+(n.time-playAnchorChart)/playSpeed;
    if(target>horizon)break;
    if(target>=audioCtx.currentTime-.015)drumAt(n.part,n.velocity,target);
    nextNote++;
  }
}
function startPlayback(){
  if(playing)return;
  ensureAudio();
  if(time>=chart.duration)time=0;
  playing=true;playSpeed=currentSpeed();
  playAnchorCtx=audioCtx.currentTime+.04;
  playAnchorChart=time;
  resetNextNote();
  startOriginal();
  scheduleAhead();
  schedulerTimer=setInterval(scheduleAhead,25);
  $("playPause").textContent="一時停止 ❚❚";
}
function pausePlayback(update=true){
  if(update&&playing)time=Math.min(chart.duration,chartTimeFromClock());
  playing=false;
  if(schedulerTimer){clearInterval(schedulerTimer);schedulerTimer=null}
  stopOriginal();stopScheduled();
  $("playPause").textContent="再生 ▶";
  updateTime();draw();
}
function toggle(){playing?pausePlayback():startPlayback()}
function seek(v){
  const was=playing;
  if(was)pausePlayback();
  time=Math.max(0,Math.min(chart.duration,v));
  resetNextNote();updateTime();draw();
  if(was)startPlayback();
}
function restartAtCurrentForSpeedChange(){
  if(!playing)return;
  const t=chartTimeFromClock();
  pausePlayback(false);time=t;startPlayback();
}
function loop(){
  if(playing){
    time=Math.min(chart.duration,chartTimeFromClock());
    if(time>=chart.duration){pausePlayback(false);time=chart.duration}
    updateTime();draw();
  }
  requestAnimationFrame(loop);
}

$("chartFile").addEventListener("change",async e=>{
  const f=e.target.files?.[0];if(!f)return;
  try{setStatus("譜面を解析しています…");setChart(await parseChart(f));setStatus(`${f.name} を読み込みました。`)}
  catch(err){setStatus(err.message)}
});
$("audioFile").addEventListener("change",async e=>{
  const f=e.target.files?.[0];if(!f)return;
  try{
    pausePlayback();
    setStatus("元音源を解析しています…");
    audioBuffer=await decodeAudio(f);
    onsets=analyzeOnsets(audioBuffer,chart.bpm);
    $("alignAudio").disabled=false;
    setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。同じWeb Audio時計で同期再生します。`);
  }catch(err){setStatus("元音源の読み込みに失敗しました: "+err.message)}
});
$("alignAudio").onclick=()=>{
  const r=realignNotes(chart.notes,onsets,chart.bpm);
  chart={...chart,notes:r.notes};
  resetNextNote();draw();
  setStatus(`音源同期補正: ${r.stats.moved}ノーツを補正、平均移動 ${r.stats.meanShiftMs.toFixed(1)}ms。`);
};
$("loadSample").onclick=()=>{setChart(makeSample());setStatus("サンプルを読み込みました。")};
$("loadLuna").onclick=async()=>{
  try{
    setStatus("Luna say maybe 完成譜面を読み込んでいます…");
    const res=await fetch("./charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json",{cache:"no-store"});
    if(!res.ok)throw new Error("完成譜面を取得できませんでした");
    const data=await res.json();
    const file=new File([JSON.stringify(data)],"Luna_say_maybe_FINAL_notes.json",{type:"application/json"});
    setChart(await parseChart(file));
    setStatus("Luna say maybe 完成譜面（Songsterr基準・元音源+1.693秒同期）を読み込みました。元音源を開くと同期再生できます。");
  }catch(err){
    setStatus("Luna say maybe 完成譜面の読み込みに失敗しました: "+err.message);
  }
};
$("exportJson").onclick=()=>{
  const safe=(chart.name||"dtx-drum-flow").replace(/[\\/:*?"<>|]+/g,"_");
  downloadText(`${safe}.json`,JSON.stringify(chartToJson(),null,2));
  setStatus("現在の譜面をJSONで保存しました。");
};
$("playPause").onclick=toggle;
$("rewind5").onclick=()=>seek(time-5);
$("forward5").onclick=()=>seek(time+5);
$("rewindMeasure").onclick=()=>seek(time-measureSeconds()*4);
$("forwardMeasure").onclick=()=>seek(time+measureSeconds()*4);
$("timeline").oninput=e=>seek(Number(e.target.value));
$("speed").onchange=restartAtCurrentForSpeedChange;

function syncSoundToggleUi(){
  $("drumSoundState").textContent=$("drumSound").checked?"ON":"OFF";
  $("originalSoundState").textContent=$("originalSound").checked?"ON":"OFF";
}
$("drumSound").onchange=()=>{
  syncSoundToggleUi();
  if(playing){resetNextNote();scheduleAhead()}
};
$("originalSound").onchange=()=>{
  syncSoundToggleUi();
  if(playing){
    const t=chartTimeFromClock();
    pausePlayback(false);time=t;startPlayback();
  }
};
$("noteSpeed").oninput=e=>{
  noteSpeed=Math.max(.5,Math.min(8,Number(e.target.value)||1));
  $("noteSpeedValue").textContent=noteSpeed.toFixed(1)+"×";
  draw();
};

for(const [sel,dir] of [[".seek-zone.left",-1],[".seek-zone.right",1]]){
  let last=0;
  document.querySelector(sel).addEventListener("pointerup",()=>{
    const now=performance.now();
    if(now-last<350)seek(time+dir*measureSeconds()*4);
    last=now;
  });
}
function measureSeconds(){return 240/(chart.bpm||120)}
addEventListener("keydown",e=>{
  if(e.target.matches("input,select"))return;
  if(e.code==="Space"){e.preventDefault();toggle()}
  if(e.code==="ArrowLeft")seek(time-5);
  if(e.code==="ArrowRight")seek(time+5);
});
const dropZone=$("dropZone");
for(const ev of ["dragenter","dragover"]){
  dropZone.addEventListener(ev,e=>{e.preventDefault();dropZone.classList.add("dragover")});
}
for(const ev of ["dragleave","drop"]){
  dropZone.addEventListener(ev,e=>{e.preventDefault();dropZone.classList.remove("dragover")});
}
dropZone.addEventListener("drop",async e=>{
  const files=[...(e.dataTransfer?.files||[])];
  for(const f of files){
    const ext=f.name.split(".").pop().toLowerCase();
    try{
      if(["mid","midi","dtx","gda","json"].includes(ext)){
        setStatus("譜面を解析しています…");setChart(await parseChart(f));setStatus(`${f.name} を読み込みました。`);
      }else if(f.type.startsWith("audio/")){
        pausePlayback();setStatus("元音源を解析しています…");
        audioBuffer=await decodeAudio(f);onsets=analyzeOnsets(audioBuffer,chart.bpm);
        $("alignAudio").disabled=false;
        setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。`);
      }
    }catch(err){setStatus(`${f.name}: ${err.message}`)}
  }
});
addEventListener("resize",resize);
makeParts();syncSoundToggleUi();setChart(chart);resize();requestAnimationFrame(loop);
