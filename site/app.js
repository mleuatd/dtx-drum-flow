import {makeSample,parseChart} from "./parsers.js";
import {decodeAudio,analyzeOnsets,realignNotes} from "./audio-analysis.js";

const PARTS=["LC","HH","SN","HT","LT","FT","RC","RD","LP","LB","BD"];
const PART_LABEL={LC:"左シンバル",HH:"ハイハット",SN:"スネア",HT:"ハイタム",LT:"ロータム",FT:"フロアタム",RC:"右シンバル",RD:"ライド",LP:"左足HH",LB:"左足BD",BD:"バスドラム"};
const $=id=>document.getElementById(id),canvas=$("laneCanvas"),ctx=canvas.getContext("2d");
let chart=makeSample(),time=0,playing=false,lastFrame=0,audioBuffer=null,onsets=[],audioCtx=null,nextNote=0;
const partEls=new Map();

function fmt(s){s=Math.max(0,s);const m=Math.floor(s/60),sec=(s%60).toFixed(1).padStart(4,"0");return `${m}:${sec}`}
function setStatus(s){$("status").textContent=s}
function setChart(c){chart=c;time=0;nextNote=0;$("timeline").max=c.duration;$("duration").textContent=fmt(c.duration);$("chartName").textContent=c.name;$("chartMeta").textContent=`${Math.round(c.bpm)} BPM · ${c.duration.toFixed(1)}秒 · ${c.notes.length}ノーツ`;draw();updateTime()}
function updateTime(){$("currentTime").textContent=fmt(time);$("timeline").value=time}
function resize(){const r=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw()}
function draw(){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const lane=w/PARTS.length;
  ctx.fillStyle="#0e172a";ctx.fillRect(0,0,w,h);ctx.strokeStyle="#223656";ctx.lineWidth=1;
  for(let i=1;i<PARTS.length;i++){ctx.beginPath();ctx.moveTo(i*lane,0);ctx.lineTo(i*lane,h);ctx.stroke()}
  const judgeY=h-36;ctx.strokeStyle="#86a7ff";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(0,judgeY);ctx.lineTo(w,judgeY);ctx.stroke();
  const lookAhead=3.3,lookBack=.35;
  for(const n of chart.notes){const dt=n.time-time;if(dt<-lookBack||dt>lookAhead)continue;const x=(PARTS.indexOf(n.part)+.5)*lane,y=judgeY-(dt/lookAhead)*(judgeY-20);ctx.beginPath();ctx.arc(x,y,Math.max(5,lane*.12),0,Math.PI*2);ctx.fillStyle=n.alignConfidence?"#8ad8ff":"#f2f5ff";ctx.fill()}
}
function makeParts(){const root=$("parts");root.innerHTML="";for(const p of PARTS){const el=document.createElement("div");el.className="part";el.innerHTML=`<strong>${p}</strong><span>${PART_LABEL[p]}</span>`;root.append(el);partEls.set(p,el)}}
function flash(part){const el=partEls.get(part);if(!el)return;el.classList.add("hit");setTimeout(()=>el.classList.remove("hit"),90)}
function ensureAudio(){audioCtx??=new (window.AudioContext||window.webkitAudioContext)();if(audioCtx.state==="suspended")audioCtx.resume()}
function drum(part,vel=.8){ensureAudio();const now=audioCtx.currentTime,g=audioCtx.createGain();g.gain.setValueAtTime(.0001,now);g.gain.exponentialRampToValueAtTime(.2*vel,now+.003);g.gain.exponentialRampToValueAtTime(.0001,now+.22);g.connect(audioCtx.destination);
  if(part==="BD"){const o=audioCtx.createOscillator();o.frequency.setValueAtTime(120,now);o.frequency.exponentialRampToValueAtTime(48,now+.12);o.connect(g);o.start(now);o.stop(now+.24)}
  else{const len=Math.round(audioCtx.sampleRate*.18),b=audioCtx.createBuffer(1,len,audioCtx.sampleRate),d=b.getChannelData(0);for(let i=0;i<len;i++)d[i]=(Math.random()*2-1)*(1-i/len);const s=audioCtx.createBufferSource();s.buffer=b;const f=audioCtx.createBiquadFilter();f.type=part==="HH"||part==="RC"||part==="RD"?"highpass":"bandpass";f.frequency.value=part==="SN"?1800:part==="HH"?6500:3200;s.connect(f);f.connect(g);s.start(now)}
  flash(part)
}
function seek(v){time=Math.max(0,Math.min(chart.duration,v));nextNote=chart.notes.findIndex(n=>n.time>=time);if(nextNote<0)nextNote=chart.notes.length;updateTime();draw()}
function measureSeconds(){return 240/(chart.bpm||120)}
function toggle(){playing=!playing;$("playPause").textContent=playing?"一時停止 ❚❚":"再生 ▶";lastFrame=performance.now();ensureAudio()}
function loop(ts){if(playing){const speed=Number($("speed").value)||1;time+=(ts-lastFrame)/1000*speed;while(nextNote<chart.notes.length&&chart.notes[nextNote].time<=time+.012){const n=chart.notes[nextNote++];drum(n.part,n.velocity);};if(time>=chart.duration){time=chart.duration;playing=false;$("playPause").textContent="再生 ▶"}updateTime();draw()}lastFrame=ts;requestAnimationFrame(loop)}

$("chartFile").addEventListener("change",async e=>{const f=e.target.files?.[0];if(!f)return;try{setStatus("譜面を解析しています…");setChart(await parseChart(f));setStatus(`${f.name} を読み込みました。`)}catch(err){setStatus(err.message)}});
$("audioFile").addEventListener("change",async e=>{const f=e.target.files?.[0];if(!f)return;try{setStatus("元音源を解析しています…");audioBuffer=await decodeAudio(f);onsets=analyzeOnsets(audioBuffer,chart.bpm);$("alignAudio").disabled=false;setStatus(`元音源を読み込みました。アタック候補 ${onsets.length} 箇所を検出しました。`)}catch(err){setStatus("元音源の読み込みに失敗しました: "+err.message)}});
$("alignAudio").onclick=()=>{const r=realignNotes(chart.notes,onsets,chart.bpm);chart={...chart,notes:r.notes};nextNote=0;seek(time);setStatus(`音源同期補正: ${r.stats.moved}ノーツを補正、平均移動 ${r.stats.meanShiftMs.toFixed(1)}ms。`)};
$("loadSample").onclick=()=>{setChart(makeSample());setStatus("サンプルを読み込みました。")};$("playPause").onclick=toggle;$("rewind5").onclick=()=>seek(time-5);$("forward5").onclick=()=>seek(time+5);$("timeline").oninput=e=>seek(Number(e.target.value));
for(const [sel,dir] of [[".seek-zone.left",-1],[".seek-zone.right",1]]){let last=0;document.querySelector(sel).addEventListener("pointerup",e=>{const now=performance.now();if(now-last<350)seek(time+dir*measureSeconds()*4);last=now})}
addEventListener("keydown",e=>{if(e.target.matches("input,select"))return;if(e.code==="Space"){e.preventDefault();toggle()}if(e.code==="ArrowLeft")seek(time-5);if(e.code==="ArrowRight")seek(time+5)});
addEventListener("resize",resize);makeParts();setChart(chart);resize();requestAnimationFrame(loop);
