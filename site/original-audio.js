const $=id=>document.getElementById(id);
const fileInput=$("audioFile"),playButton=$("playPause"),timeline=$("timeline"),speed=$("speed");
const legacy=$("originalSound"),legacyLabel=legacy?.closest("label");
const audio=new Audio();audio.preload="auto";audio.playsInline=true;
let objectUrl="",loaded=false,fullMixToggle=null,fullMixState=null;
function installToggle(){
  if(!legacyLabel)return;
  legacy.checked=false;legacy.dispatchEvent(new Event("change",{bubbles:true}));legacyLabel.hidden=true;
  const label=document.createElement("label");label.className="sound-toggle";
  label.innerHTML='<input id="fullMixSound" type="checkbox" checked><span>原曲（全楽器）</span><strong id="fullMixSoundState">ON</strong>';
  legacyLabel.after(label);fullMixToggle=label.querySelector("input");fullMixState=label.querySelector("strong");
  fullMixToggle.addEventListener("change",()=>{fullMixState.textContent=fullMixToggle.checked?"ON":"OFF";if(!fullMixToggle.checked)audio.pause();else syncPlayback()});
}
function chartTime(){return Math.max(0,Number(timeline?.value)||0)}
function syncPosition(force=false){
  if(!loaded)return;const target=Math.min(chartTime(),Math.max(0,(audio.duration||Infinity)-.01));
  if(force||Math.abs((audio.currentTime||0)-target)>.12){try{audio.currentTime=target}catch{}}
}
async function syncPlayback(){
  if(!loaded||!fullMixToggle?.checked)return;
  audio.playbackRate=Math.max(.25,Math.min(4,Number(speed?.value)||1));syncPosition();
  const isPlaying=playButton?.textContent?.includes("一時停止");
  if(isPlaying){try{await audio.play()}catch(err){$("status").textContent="原曲の再生開始に失敗しました。再生ボタンをもう一度押してください: "+err.message}}
  else audio.pause();
}
fileInput?.addEventListener("change",e=>{
  const f=e.target.files?.[0];if(!f)return;audio.pause();if(objectUrl)URL.revokeObjectURL(objectUrl);
  objectUrl=URL.createObjectURL(f);audio.src=objectUrl;audio.load();loaded=true;
  audio.addEventListener("loadedmetadata",()=>{syncPosition(true);$("status").textContent=`原曲（全楽器）を読み込みました: ${f.name}。再生ボタンで譜面と同時再生します。`;},{once:true});
});
playButton?.addEventListener("click",()=>setTimeout(syncPlayback,0));
timeline?.addEventListener("input",()=>{syncPosition(true);setTimeout(syncPlayback,0)});
speed?.addEventListener("change",()=>{audio.playbackRate=Math.max(.25,Math.min(4,Number(speed.value)||1));syncPosition(true);setTimeout(syncPlayback,0)});\naddEventListener("dtx-chart-change",()=>{audio.pause();loaded=false;if(objectUrl){URL.revokeObjectURL(objectUrl);objectUrl=""}audio.removeAttribute("src");audio.load();if(fullMixState)fullMixState.textContent=fullMixToggle?.checked?"ON":"OFF"});
for(const id of ["rewind5","forward5","rewindMeasure","forwardMeasure"]){$(id)?.addEventListener("click",()=>setTimeout(()=>{syncPosition(true);syncPlayback()},0))}
audio.addEventListener("error",()=>{$("status").textContent="原曲（全楽器）の再生に失敗しました。端末で再生できる MP3 / M4A / WAV を選んでください。"});
addEventListener("beforeunload",()=>{if(objectUrl)URL.revokeObjectURL(objectUrl)});
installToggle();
