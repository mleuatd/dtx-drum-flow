const $=id=>document.getElementById(id);
const fileInput=$("audioFile"),playButton=$("playPause"),timeline=$("timeline"),speed=$("speed");
const legacy=$("originalSound"),legacyLabel=legacy?.closest("label");
const audio=new Audio();audio.preload="auto";audio.playsInline=true;
let objectUrl="",loaded=false,fullMixToggle=null,fullMixState=null,activeChartKey="luna";

const DB_NAME="dtx-drum-flow-audio",DB_STORE="audio";
function chartKeyFromName(name=""){if(name.includes("叶えたい"))return "kanaetai";if(name.includes("一体いつから"))return "ittai";return "luna"}
function openDb(){return new Promise((resolve,reject)=>{const req=indexedDB.open(DB_NAME,1);req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains(DB_STORE))db.createObjectStore(DB_STORE)};req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
async function saveLocalAudio(key,file){try{const db=await openDb();await new Promise((resolve,reject)=>{const tx=db.transaction(DB_STORE,"readwrite");tx.objectStore(DB_STORE).put(file,key);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)});db.close()}catch{}}
async function getLocalAudio(key){try{const db=await openDb();const value=await new Promise((resolve,reject)=>{const tx=db.transaction(DB_STORE,"readonly"),req=tx.objectStore(DB_STORE).get(key);req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)});db.close();return value||null}catch{return null}}
function loadAudioBlob(blob,label){audio.pause();if(objectUrl)URL.revokeObjectURL(objectUrl);objectUrl=URL.createObjectURL(blob);audio.src=objectUrl;audio.load();loaded=true;audio.addEventListener("loadedmetadata",()=>{syncPosition(true);$("status").textContent=`${label} を読み込みました。再生ボタンで譜面と同期再生します。`;},{once:true})}
async function restoreLocalAudio(){const saved=await getLocalAudio(activeChartKey);if(saved)loadAudioBlob(saved,"端末に保存済みの原曲")}

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
fileInput?.addEventListener("change",async e=>{
  const f=e.target.files?.[0];if(!f)return;
  loadAudioBlob(f,`原曲（全楽器）: ${f.name}`);
  await saveLocalAudio(activeChartKey,f);
  $("status").textContent=`原曲を端末内に保存しました: ${f.name}。次回からこの曲で自動復元します。`;
});
playButton?.addEventListener("click",()=>setTimeout(syncPlayback,0));
timeline?.addEventListener("input",()=>{syncPosition(true);setTimeout(syncPlayback,0)});
speed?.addEventListener("change",()=>{audio.playbackRate=Math.max(.25,Math.min(4,Number(speed.value)||1));syncPosition(true);setTimeout(syncPlayback,0)});
addEventListener("dtx-chart-change",async e=>{audio.pause();loaded=false;if(objectUrl){URL.revokeObjectURL(objectUrl);objectUrl=""}audio.removeAttribute("src");audio.load();activeChartKey=chartKeyFromName(e.detail?.name||"");if(fullMixState)fullMixState.textContent=fullMixToggle?.checked?"ON":"OFF";await restoreLocalAudio()});
for(const id of ["rewind5","forward5","rewindMeasure","forwardMeasure"]){$(id)?.addEventListener("click",()=>setTimeout(()=>{syncPosition(true);syncPlayback()},0))}
audio.addEventListener("error",()=>{$("status").textContent="原曲（全楽器）の再生に失敗しました。端末で再生できる MP3 / M4A / WAV を選んでください。"});
addEventListener("beforeunload",()=>{if(objectUrl)URL.revokeObjectURL(objectUrl)});
installToggle();

restoreLocalAudio();
