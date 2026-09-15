import {makeSample,parseChart} from "./parsers.js";
import {decodeAudio,analyzeOnsets,realignNotes} from "./audio-analysis.js";

const PARTS=["LC","HH","SN","HT","LT","FT","RC","RD","LP","LB","BD"];
const PART_LABEL={LC:"左シンバル",HH:"ハイハット",SN:"スネア",HT:"ハイタム",LT:"ロータム",FT:"フロアタム",RC:"右シンバル",RD:"ライド",LP:"左足HH",LB:"左足BD",BD:"バスドラム"};
const PART_ICON={LC:"◯",HH:"◎",SN:"🥁",HT:"◒",LT:"◓",FT:"◉",RC:"◯",RD:"◌",LP:"⌁",LB:"●",BD:"⬤"};
const $=id=>document.getElementById(id),canvas=$("laneCanvas"),ctx=canvas.getContext("2d");
let chart=makeSample(),time=0,playing=false,audioBuffer=null,onsets=[],audioCtx=null,originalSource=null,schedulerTimer=null,scheduledNodes=[],nextNote=0,playAnchorCtx=0,playAnchorChart=0,playSpeed=1,noteSpeed=1;
const partEls=new Map();
const clampTime=v=>Math.max(0,Math.min(chart.duration,Number(v)||0));
function fmt(s){s=Math.max(0,s);const m=Math.floor(s/60),sec=(s%60).toFixed(1).padStart(4,"0");return `${m}:${sec}`}
function setStatus(s){$("status").textContent=s}
function downloadText(name,text,type="application/json"){const blob=new Blob([text],{type}),url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),500)}
function chartToJson(){const partKind={BD:"kick",LB:"kick",SN:"snare",HH:"hihat",LP:"hihat",HT:"toms",LT:"toms",FT:"toms",LC:"cymbals",RC:"cymbals",RD:"cymbals"};return {...chart,notes:chart.notes.map(n=>({...n,time:Number(n.time.toFixed(6)),kind:n.kind||partKind[n.part]||"unknown",part:n.part,velocity:Math.round(Math.max(0,Math.min(1,n.velocity??.8))*127),confidence:Number(n.alignConfidence??n.confidence??0)}))}}
function currentSpeed(){return Number($("speed").value)||1}
function setChart(c){pausePlayback(false);chart=c;time=0;nextNote=0;$("timeline").max=c.duration;$("duration").textContent=fmt(c.duration);$("chartName").textContent=c.name;$("chartMeta").textContent=`${Math.round(c.bpm)} BPM · ${c.duration.toFixed(1)}秒 · ${c.notes.length.toLocaleString()}ノーツ`;const kana=(c.name||"").includes("叶えたい");if($("stageTitle"))$("stageTitle").textContent=kana?"叶えたい、ことばかり / DRUM CHART":"LUNA / DRUM CHART";if($("chartBadge"))$("chartBadge").textContent=kana?"KANAETAI FINAL":"LUNA FINAL";draw();updateTime()}
function updateTime(){$("currentTime").textContent=fmt(time);const mirror=$("currentTimeMirror");if(mirror)mirror.textContent=fmt(time);$("timeline").value=time}
function resize(){const r=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw()}
function draw(){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const lane=w/PARTS.length;ctx.fillStyle="#0e172a";ctx.fillRect(0,0,w,h);ctx.strokeStyle="#223656";ctx.lineWidth=1;for(let i=1;i<PARTS.length;i++){ctx.beginPath();ctx.moveTo(i*lane,0);ctx.lineTo(i*lane,h);ctx.stroke()}const judgeY=h-36,lookAhead=3.3/noteSpeed;const hitNow=chart.notes.some(n=>Math.abs(n.time-time)<=Math.max(.025,.04/currentSpeed()));ctx.save();ctx.strokeStyle=hitNow?"#ffffff":"#86a7ff";ctx.shadowColor=hitNow?"#9fc5ff":"transparent";ctx.shadowBlur=hitNow?22:0;ctx.lineWidth=hitNow?5:3;ctx.beginPath();ctx.moveTo(0,judgeY);ctx.lineTo(w,judgeY);ctx.stroke();ctx.restore();for(const n of chart.notes){const dt=n.time-time;if(dt<0||dt>lookAhead)continue;const x=(PARTS.indexOf(n.part)+.5)*lane,y=judgeY-(dt/lookAhead)*(judgeY-20),conf=Number(n.alignConfidence||0),radius=Math.max(5,lane*.12)*(conf>0?(.78+.22*conf):1);ctx.globalAlpha=conf>0?Math.max(.35,conf):1;ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.fillStyle=conf>0?(conf>=.65?"#8ad8ff":conf>=.35?"#f0d889":"#e59696"):"#f2f5ff";ctx.fill();ctx.globalAlpha=1}}
function makeParts(){const root=$("parts");root.innerHTML="";for(const p of PARTS){const el=document.createElement("div");el.className="part";el.innerHTML=`<span class="icon" aria-hidden="true">${PART_ICON[p]}</span><strong>${p}</strong><span class="label">${PART_LABEL[p]}</span>`;root.append(el);partEls.set(p,el)}}
function flash(part){const el=partEls.get(part);if(!el)return;el.classList.add("hit");setTimeout(()=>el.classList.remove("hit"),90)}
async function ensureAudio(){audioCtx??=new (window.AudioContext||window.webkitAudioContext)({latencyHint:"interactive"});if(audioCtx.state==="suspended")await audioCtx.resume();return audioCtx}
function trackNode(node){scheduledNodes.push(node);node.addEventListener?.("ended",()=>{scheduledNodes=scheduledNodes.filter(x=>x!==node)},{once:true})}
function stopScheduled(){for(const n of scheduledNodes){try{n.stop()}catch{}}scheduledNodes=[]}
function noiseBuffer(seconds=.25){const len=Math.max(1,Math.round(audioCtx.sampleRate*seconds)),b=audioCtx.createBuffer(1,len,audioCtx.sampleRate),d=b.getChannelData(0);for(let i=0;i<len;i++)d[i]=Math.random()*2-1;return b}
function gainEnv(t,peak,attack,decay){const g=audioCtx.createGain();g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(Math.max(.0002,peak),t+attack);g.gain.exponentialRampToValueAtTime(.0001,t+decay);g.connect(audioCtx.destination);return g}
function tone(freq,t,dur,gain,type="sine",endFreq=null){const o=audioCtx.createOscillator(),g=gainEnv(t,gain,.002,dur);o.type=type;o.frequency.setValueAtTime(freq,t);if(endFreq)o.frequency.exponentialRampToValueAtTime(endFreq,t+dur*.7);o.connect(g);o.start(t);o.stop(t+dur+.02);trackNode(o)}
function filteredNoise(t,dur,gain,type,freq,q=.7){const s=audioCtx.createBufferSource(),f=audioCtx.createBiquadFilter(),g=gainEnv(t,gain,.001,dur);s.buffer=noiseBuffer(dur+.03);f.type=type;f.frequency.value=freq;f.Q.value=q;s.connect(f);f.connect(g);s.start(t);s.stop(t+dur+.03);trackNode(s)}
function drumAt(part,vel=.8,when=null,note=null){
  if(!$("drumSound").checked||!audioCtx)return;
  const t=Math.max(audioCtx.currentTime+.002,when??audioCtx.currentTime+.002),v=Math.max(.18,Math.min(1,vel||.8)),gm=Number(note?.gmNote);
  if((part==="SN")&&gm===37){
    /* Luna 2番Aメロのサイドスティック/クロススティック。短い木質の「カッ」。 */
    tone(920,t,.045,.19*v,"triangle",760);tone(1680,t+.001,.025,.08*v,"sine",1450);filteredNoise(t,.035,.055*v,"bandpass",2300,3.5);
  }else if(part==="BD"||part==="LB"){
    tone(105,t,.19,.42*v,"sine",45);tone(170,t,.055,.10*v,"triangle",70);filteredNoise(t,.025,.045*v,"highpass",3200,.5);
  }else if(part==="SN"){
    tone(185,t,.13,.14*v,"triangle",125);filteredNoise(t,.16,.30*v,"bandpass",1900,.8);filteredNoise(t,.055,.09*v,"highpass",6200,.5);
  }else if(part==="HH"||part==="LP"){
    const open=gm===46,dur=open?.42:.075;filteredNoise(t,dur,.16*v,"highpass",6800,.45);tone(8600,t,open?.18:.045,.025*v,"square",open?6200:7200);
  }else if(part==="HT"||part==="LT"||part==="FT"){
    const f=part==="HT"?175:part==="LT"?135:95;tone(f,t,.27,.30*v,"sine",f*.72);filteredNoise(t,.07,.075*v,"bandpass",part==="HT"?1500:part==="LT"?1150:850,1.2);
  }else if(part==="RD"){
    tone(3100,t,.42,.055*v,"triangle",2600);filteredNoise(t,.34,.095*v,"highpass",5200,.5);
  }else{
    /* crash / left cymbal: bright attack + long metallic wash */
    filteredNoise(t,.85,.17*v,"highpass",4200,.4);tone(4700,t,.52,.035*v,"square",3300);tone(7100,t,.36,.022*v,"square",5200);
  }
  setTimeout(()=>flash(part),Math.max(0,(t-audioCtx.currentTime)*1000));
}
function stopOriginal(){if(originalSource){try{originalSource.stop()}catch{}originalSource=null}}
function startOriginal(){stopOriginal();if(!audioBuffer||!$("originalSound").checked||!audioCtx)return;const offset=Math.max(0,Math.min(playAnchorChart,audioBuffer.duration-.001));if(offset>=audioBuffer.duration)return;originalSource=audioCtx.createBufferSource();originalSource.buffer=audioBuffer;originalSource.playbackRate.value=playSpeed;originalSource.connect(audioCtx.destination);originalSource.start(playAnchorCtx,offset)}
function chartTimeFromClock(){if(!playing||!audioCtx)return clampTime(time);const elapsed=Math.max(0,audioCtx.currentTime-playAnchorCtx);return clampTime(playAnchorChart+elapsed*playSpeed)}
function resetNextNote(at=time){const t=clampTime(at);nextNote=chart.notes.findIndex(n=>n.time>=t-.005);if(nextNote<0)nextNote=chart.notes.length}
function scheduleAhead(){if(!playing||!audioCtx)return;const horizon=audioCtx.currentTime+.12;while(nextNote<chart.notes.length){const n=chart.notes[nextNote],target=playAnchorCtx+(n.time-playAnchorChart)/playSpeed;if(target>horizon)break;if(target>=audioCtx.currentTime-.03)drumAt(n.part,n.velocity,target,n);nextNote++}}
async function startPlayback(){if(playing)return;await ensureAudio();if(time>=chart.duration)time=0;time=clampTime(time);playing=true;playSpeed=currentSpeed();playAnchorCtx=audioCtx.currentTime+.05;playAnchorChart=time;resetNextNote(playAnchorChart);startOriginal();scheduleAhead();schedulerTimer=setInterval(scheduleAhead,20);$("playPause").textContent="一時停止 ❚❚"}
function pausePlayback(update=true){if(update&&playing)time=chartTimeFromClock();playing=false;if(schedulerTimer){clearInterval(schedulerTimer);schedulerTimer=null}stopOriginal();stopScheduled();$("playPause").textContent="再生 ▶";updateTime();draw()}
function toggle(){playing?pausePlayback():startPlayback()}
function seek(v){const was=playing;if(was)pausePlayback();time=clampTime(v);resetNextNote(time);updateTime();draw();if(was)startPlayback()}
function restartPlaybackAtClock(){if(!playing)return;const t=chartTimeFromClock();pausePlayback(false);time=clampTime(t);startPlayback()}
function loop(){if(playing){time=chartTimeFromClock();if(time>=chart.duration){pausePlayback(false);time=chart.duration;updateTime();draw()}else{updateTime();draw()}}requestAnimationFrame(loop)}

$("chartFile").addEventListener("change",async e=>{const f=e.target.files?.[0];if(!f)return;try{setStatus("譜面を解析しています…");setChart(await parseChart(f));setStatus(`${f.name} を読み込みました。`)}catch(err){setStatus(err.message)}});
$("audioFile").addEventListener("change",async e=>{const f=e.target.files?.[0];if(!f)return;try{pausePlayback();setStatus("元音源を解析しています…");audioBuffer=await decodeAudio(f);onsets=analyzeOnsets(audioBuffer,chart.bpm);$("alignAudio").disabled=false;setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。同じWeb Audio時計で同期再生します。`)}catch(err){setStatus("元音源の読み込みに失敗しました: "+err.message)}});
$("alignAudio").onclick=()=>{const was=playing,t=was?chartTimeFromClock():time;if(was)pausePlayback(false);const r=realignNotes(chart.notes,onsets,chart.bpm);chart={...chart,notes:r.notes};time=clampTime(t);resetNextNote(time);draw();if(was)startPlayback();setStatus(`音源同期補正: ${r.stats.moved}ノーツを補正、平均移動 ${r.stats.meanShiftMs.toFixed(1)}ms。`)};
$("loadSample").onclick=()=>{setChart(makeSample());setStatus("サンプルを読み込みました。")};
async function loadFinalChart({label,path,fileName,status}){try{setStatus(label+" 完成譜面を読み込んでいます…");const res=await fetch(path,{cache:"no-store"});if(!res.ok)throw new Error("完成譜面を取得できませんでした (HTTP "+res.status+")");const data=await res.json(),file=new File([JSON.stringify(data)],fileName,{type:"application/json"});window.dispatchEvent(new CustomEvent("dtx-chart-change",{detail:{name:data.name||label}}));setChart(await parseChart(file));setStatus(status)}catch(err){setStatus(label+" 完成譜面の読み込みに失敗しました: "+err.message)}}
$("loadLuna").onclick=()=>loadFinalChart({label:"Luna say maybe",path:"./charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json",fileName:"Luna_say_maybe_FINAL_notes.json",status:"Luna say maybe 完成譜面（Songsterr基準・元音源+1.693秒同期）を読み込みました。リアルドラム音色（2番Aメロのサイドスティック含む）で再生できます。"});
$("loadKanaetai").onclick=()=>loadFinalChart({label:"叶えたい、ことばかり",path:"./charts/kanaetai_koto_bakari/Kanaetai_koto_bakari_FINAL_notes.json",fileName:"Kanaetai_koto_bakari_FINAL_notes.json",status:"叶えたい、ことばかり FINAL譜面（Songsterr s2808958 rev 3694097 Drums・全144小節）を読み込みました。原曲音源との最終ミリ秒同期のみ未実施です。"});
$("exportJson").onclick=()=>{const safe=(chart.name||"dtx-drum-flow").replace(/[\\/:*?"<>|]+/g,"_");downloadText(`${safe}.json`,JSON.stringify(chartToJson(),null,2));setStatus("現在の譜面をJSONで保存しました。")};
$("playPause").onclick=toggle;$("rewind5").onclick=()=>seek(chartTimeFromClock()-5);$("forward5").onclick=()=>seek(chartTimeFromClock()+5);$("rewindMeasure").onclick=()=>seek(chartTimeFromClock()-measureSeconds()*4);$("forwardMeasure").onclick=()=>seek(chartTimeFromClock()+measureSeconds()*4);$("timeline").oninput=e=>seek(Number(e.target.value));$("speed").onchange=restartPlaybackAtClock;
function syncSoundToggleUi(){$("drumSoundState").textContent=$("drumSound").checked?"ON":"OFF";$("originalSoundState").textContent=$("originalSound").checked?"ON":"OFF"}
$("drumSound").onchange=()=>{syncSoundToggleUi();if(playing)restartPlaybackAtClock()};$("originalSound").onchange=()=>{syncSoundToggleUi();if(playing)restartPlaybackAtClock()};
$("noteSpeed").oninput=e=>{noteSpeed=Math.max(.5,Math.min(8,Number(e.target.value)||1));$("noteSpeedValue").textContent=noteSpeed.toFixed(1)+"×";draw()};
for(const [sel,dir] of [[".seek-zone.left",-1],[".seek-zone.right",1]]){let last=0;document.querySelector(sel).addEventListener("pointerup",()=>{const now=performance.now();if(now-last<350)seek(chartTimeFromClock()+dir*measureSeconds()*4);last=now})}
function measureSeconds(){return 240/(chart.bpm||120)}
addEventListener("keydown",e=>{if(e.target.matches("input,select"))return;if(e.code==="Space"){e.preventDefault();toggle()}if(e.code==="ArrowLeft")seek(chartTimeFromClock()-5);if(e.code==="ArrowRight")seek(chartTimeFromClock()+5)});
const dropZone=$("dropZone");for(const ev of ["dragenter","dragover"]){dropZone.addEventListener(ev,e=>{e.preventDefault();dropZone.classList.add("dragover")})}for(const ev of ["dragleave","drop"]){dropZone.addEventListener(ev,e=>{e.preventDefault();dropZone.classList.remove("dragover")})}
dropZone.addEventListener("drop",async e=>{const files=[...(e.dataTransfer?.files||[])];for(const f of files){const ext=f.name.split(".").pop().toLowerCase();try{if(["mid","midi","dtx","gda","json"].includes(ext)){setStatus("譜面を解析しています…");setChart(await parseChart(f));setStatus(`${f.name} を読み込みました。`)}else if(f.type.startsWith("audio/")){pausePlayback();setStatus("元音源を解析しています…");audioBuffer=await decodeAudio(f);onsets=analyzeOnsets(audioBuffer,chart.bpm);$("alignAudio").disabled=false;setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。`)}}catch(err){setStatus(`${f.name}: ${err.message}`)}}});
addEventListener("resize",resize);makeParts();syncSoundToggleUi();setChart(chart);resize();requestAnimationFrame(loop);$("loadLuna").click();