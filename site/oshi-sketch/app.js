const rough=document.getElementById('rough');
const rctx=rough.getContext('2d');
const objectCanvas=document.getElementById('objects');
const objctx=objectCanvas.getContext('2d');
const result=document.getElementById('result');
const octx=result.getContext('2d');

let drawing=false,erasing=false,last=null;
let undoStack=[],redoStack=[],historyItems=[];
let activeHistoryIndex=-1,objectMode=null,objects=[];
let pressTimer=null,pressedObjectIndex=-1,draggingObjectIndex=-1,pressStart=null;
const LONG_PRESS_MS=420;

function white(ctx,canvas){ctx.save();ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.restore();}
function setStatus(s){document.getElementById('status').textContent=s;}
function deep(v){return JSON.parse(JSON.stringify(v));}
function snapshot(){return {rough:rough.toDataURL(),objects:deep(objects)};}
function pushUndo(){undoStack.push(snapshot());if(undoStack.length>30)undoStack.shift();redoStack=[];}
function restore(state){const img=new Image();img.onload=()=>{rctx.clearRect(0,0,800,800);rctx.drawImage(img,0,0);};img.src=state.rough;objects=deep(state.objects||[]);renderObjects();}
function pos(e){const rect=objectCanvas.getBoundingClientRect();return{x:(e.clientX-rect.left)*800/rect.width,y:(e.clientY-rect.top)*800/rect.height};}
function hitObject(x,y){for(let i=objects.length-1;i>=0;i--){const o=objects[i];if(Math.hypot(x-o.x,y-o.y)<95*(o.scale||1))return i;}return -1;}

function start(e){
 e.preventDefault();const p=pos(e);
 if(objectMode){pushUndo();objects.push({type:objectMode,x:p.x,y:p.y,scale:1});renderObjects();setStatus(objectMode==='ojika'?'小鹿さんマークを配置しました。':'人物マークを配置しました。');objectMode=null;return;}
 const hit=hitObject(p.x,p.y);
 if(hit>=0){pressedObjectIndex=hit;pressStart=p;pressTimer=setTimeout(()=>{pushUndo();draggingObjectIndex=hit;renderObjects();setStatus('長押し選択中。薄いオブジェクトを移動できます。');},LONG_PRESS_MS);return;}
 pushUndo();drawing=true;last=p;
}
function move(e){
 const p=pos(e);
 if(draggingObjectIndex>=0){e.preventDefault();objects[draggingObjectIndex].x=p.x;objects[draggingObjectIndex].y=p.y;renderObjects();return;}
 if(pressTimer&&pressStart&&Math.hypot(p.x-pressStart.x,p.y-pressStart.y)>18){clearTimeout(pressTimer);pressTimer=null;}
 if(!drawing)return;e.preventDefault();
 rctx.save();rctx.lineCap='round';rctx.lineJoin='round';rctx.lineWidth=erasing?28:5;rctx.strokeStyle=erasing?'#fff':'#111';rctx.beginPath();rctx.moveTo(last.x,last.y);rctx.lineTo(p.x,p.y);rctx.stroke();rctx.restore();last=p;
}
function end(){
 if(pressTimer){clearTimeout(pressTimer);pressTimer=null;}
 if(draggingObjectIndex>=0){draggingObjectIndex=-1;pressedObjectIndex=-1;pressStart=null;renderObjects();setStatus('オブジェクトの移動を確定しました。');}
 drawing=false;last=null;
}

function drawPersonMarker(ctx,x,y,s){
 ctx.save();ctx.strokeStyle='#111';ctx.lineWidth=7*s;ctx.lineCap='round';
 ctx.beginPath();ctx.arc(x,y-45*s,24*s,0,Math.PI*2);ctx.stroke();
 ctx.beginPath();ctx.moveTo(x,y-20*s);ctx.lineTo(x,y+40*s);ctx.moveTo(x,y);ctx.lineTo(x-32*s,y+20*s);ctx.moveTo(x,y);ctx.lineTo(x+32*s,y+20*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x-26*s,y+82*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x+26*s,y+82*s);ctx.stroke();ctx.restore();
}
function drawOjikaMarker(ctx,x,y,s){
 ctx.save();ctx.strokeStyle='#111';ctx.fillStyle='#fff';ctx.lineWidth=5*s;ctx.lineCap='round';
 const cy=y-45*s;
 for(let i=0;i<12;i++){const a=i*Math.PI/6;ctx.beginPath();ctx.ellipse(x+Math.cos(a)*36*s,cy+Math.sin(a)*36*s,10*s,18*s,a,0,Math.PI*2);ctx.stroke();}
 ctx.beginPath();ctx.arc(x,cy,23*s,0,Math.PI*2);ctx.fill();ctx.stroke();
 ctx.fillStyle='#111';ctx.font=(18*s)+'px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('小鹿',x,cy);
 ctx.beginPath();ctx.moveTo(x,y-20*s);ctx.lineTo(x,y+40*s);ctx.moveTo(x,y);ctx.lineTo(x-32*s,y+20*s);ctx.moveTo(x,y);ctx.lineTo(x+32*s,y+20*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x-26*s,y+82*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x+26*s,y+82*s);ctx.stroke();ctx.restore();
}
function renderObjects(){objctx.clearRect(0,0,800,800);objects.forEach((o,i)=>{objctx.save();if(i===draggingObjectIndex)objctx.globalAlpha=.42;(o.type==='ojika'?drawOjikaMarker:drawPersonMarker)(objctx,o.x,o.y,o.scale||1);objctx.restore();});}
function renderObjectIcons(){const a=document.getElementById('ojikaIcon'),ac=a.getContext('2d');white(ac,a);drawOjikaMarker(ac,a.width/2,82,.55);const b=document.getElementById('personIcon'),bc=b.getContext('2d');white(bc,b);drawPersonMarker(bc,b.width/2,82,.55);}

function getSettings(){
 const all=(document.getElementById('description').value+' '+document.getElementById('cleanInstruction').value+' '+document.getElementById('revision').value).toLowerCase();
 let expression=document.getElementById('expressionPreset').value;
 let hair=document.getElementById('hairPreset').value;
 if(/虚無感マシマシ|虚無.*強|目.*線/.test(all))expression='void-max';else if(/虚無|無表情|感情がない|心を失/.test(all))expression='void';else if(/笑顔|笑って/.test(all))expression='smile';else if(/驚|びっくり/.test(all))expression='surprised';
 if(/ツインテール/.test(all))hair='twin';else if(/ひとつ結び|ポニーテール/.test(all))hair='pony';else if(/ハーフアップ/.test(all))hair='half';
 return{finish:Number(document.getElementById('finishRange').value),expression,hair,text:all};
}

function lineStyle(ctx,finish){ctx.strokeStyle='#111';ctx.fillStyle='#fff';ctx.lineCap='round';ctx.lineJoin='round';ctx.lineWidth=finish<30?3.6:finish>75?2.0:2.8;}
function drawFace(ctx,x,y,s,exp){
 ctx.beginPath();
 if(exp==='void-max'){ctx.moveTo(x-13*s,y);ctx.lineTo(x-5*s,y);ctx.moveTo(x+5*s,y);ctx.lineTo(x+13*s,y);ctx.moveTo(x-2*s,y+13*s);ctx.lineTo(x+2*s,y+13*s);}
 else if(exp==='void'){ctx.moveTo(x-13*s,y);ctx.lineTo(x-6*s,y+1*s);ctx.moveTo(x+6*s,y+1*s);ctx.lineTo(x+13*s,y);ctx.moveTo(x-2*s,y+12*s);ctx.lineTo(x+2*s,y+12*s);}
 else if(exp==='smile'){ctx.arc(x-9*s,y,4*s,0,Math.PI);ctx.arc(x+9*s,y,4*s,0,Math.PI);ctx.arc(x,y+9*s,7*s,0,Math.PI);}
 else if(exp==='surprised'){ctx.arc(x-9*s,y,2.8*s,0,Math.PI*2);ctx.arc(x+9*s,y,2.8*s,0,Math.PI*2);ctx.arc(x,y+12*s,3*s,0,Math.PI*2);}
 else{ctx.arc(x-9*s,y,2.3*s,0,Math.PI*2);ctx.arc(x+9*s,y,2.3*s,0,Math.PI*2);ctx.moveTo(x-3*s,y+12*s);ctx.lineTo(x+3*s,y+12*s);}
 ctx.stroke();
}
function drawHair(ctx,x,y,s,hair){
 ctx.beginPath();ctx.arc(x,y-3*s,31*s,Math.PI*.95,Math.PI*2.05);
 if(hair==='twin'){ctx.moveTo(x-24*s,y-8*s);ctx.quadraticCurveTo(x-48*s,y+2*s,x-39*s,y+28*s);ctx.moveTo(x+24*s,y-8*s);ctx.quadraticCurveTo(x+48*s,y+2*s,x+39*s,y+28*s);}
 else if(hair==='pony'){ctx.moveTo(x+24*s,y-5*s);ctx.quadraticCurveTo(x+55*s,y+10*s,x+36*s,y+44*s);}
 else{ctx.moveTo(x-24*s,y);ctx.lineTo(x-29*s,y+44*s);ctx.moveTo(x+24*s,y);ctx.lineTo(x+29*s,y+44*s);}
 ctx.stroke();
 ctx.beginPath();ctx.moveTo(x-20*s,y-18*s);ctx.quadraticCurveTo(x-8*s,y-8*s,x-4*s,y-20*s);ctx.moveTo(x-2*s,y-20*s);ctx.quadraticCurveTo(x+8*s,y-8*s,x+18*s,y-17*s);ctx.stroke();
}
function drawOjikaFinal(ctx,x,y,s,settings,onLoop){
 ctx.save();lineStyle(ctx,settings.finish);
 const headY=y-50*s;
 ctx.beginPath();ctx.arc(x,headY,28*s,0,Math.PI*2);ctx.fill();ctx.stroke();drawHair(ctx,x,headY,s,settings.hair);drawFace(ctx,x,headY,s,settings.expression);
 ctx.beginPath();
 if(onLoop){
   ctx.moveTo(x,headY+28*s);ctx.lineTo(x,y+35*s);
   ctx.moveTo(x,y-2*s);ctx.lineTo(x-28*s,y+20*s);
   ctx.moveTo(x,y-2*s);ctx.lineTo(x+36*s,y+14*s);
   ctx.moveTo(x,y+35*s);ctx.lineTo(x-13*s,y+72*s);
   ctx.moveTo(x,y+35*s);ctx.lineTo(x+12*s,y+72*s);
 }else{
   ctx.moveTo(x,headY+28*s);ctx.lineTo(x,y+40*s);ctx.moveTo(x,y);ctx.lineTo(x-30*s,y+22*s);ctx.moveTo(x,y);ctx.lineTo(x+30*s,y+22*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x-22*s,y+82*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x+22*s,y+82*s);
 }
 ctx.stroke();ctx.restore();
}
function drawOtherFinal(ctx,x,y,s,finish){ctx.save();lineStyle(ctx,finish);ctx.beginPath();ctx.arc(x,y-44*s,23*s,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(x,y-20*s);ctx.lineTo(x,y+40*s);ctx.moveTo(x,y);ctx.lineTo(x-28*s,y+20*s);ctx.moveTo(x,y);ctx.lineTo(x+28*s,y+20*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x-22*s,y+80*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x+22*s,y+80*s);ctx.stroke();ctx.restore();}
function drawLoop(ctx,x,y,s,finish){
 ctx.save();lineStyle(ctx,finish);ctx.beginPath();ctx.arc(x-24*s,y+30*s,18*s,0,Math.PI*2);ctx.arc(x+38*s,y+30*s,18*s,0,Math.PI*2);ctx.moveTo(x-24*s,y+12*s);ctx.lineTo(x+26*s,y+12*s);ctx.lineTo(x+14*s,y-54*s);ctx.moveTo(x+14*s,y-54*s);ctx.lineTo(x+42*s,y-54*s);ctx.stroke();ctx.restore();
}
function drawDog(ctx,x,y,s,finish){
 ctx.save();lineStyle(ctx,finish);ctx.beginPath();ctx.ellipse(x,y,36*s,23*s,-.08,0,Math.PI*2);ctx.stroke();
 ctx.beginPath();ctx.arc(x+38*s,y-18*s,18*s,0,Math.PI*2);ctx.stroke();
 ctx.beginPath();ctx.moveTo(x+27*s,y-31*s);ctx.lineTo(x+22*s,y-48*s);ctx.lineTo(x+35*s,y-36*s);ctx.moveTo(x+48*s,y-29*s);ctx.lineTo(x+55*s,y-45*s);ctx.lineTo(x+58*s,y-27*s);ctx.stroke();
 ctx.beginPath();ctx.moveTo(x-24*s,y+17*s);ctx.lineTo(x-28*s,y+48*s);ctx.moveTo(x+5*s,y+20*s);ctx.lineTo(x+6*s,y+49*s);ctx.moveTo(x-34*s,y-5*s);ctx.quadraticCurveTo(x-56*s,y-25*s,x-48*s,y-43*s);ctx.stroke();
 ctx.beginPath();ctx.arc(x+42*s,y-19*s,2*s,0,Math.PI*2);ctx.fillStyle='#111';ctx.fill();ctx.restore();
}
function drawLeash(ctx,x1,y1,x2,y2,finish){ctx.save();lineStyle(ctx,finish);ctx.beginPath();ctx.moveTo(x1,y1);ctx.quadraticCurveTo((x1+x2)/2,y1+35,x2,y2);ctx.stroke();ctx.restore();}
function drawBackground(ctx,finish){ctx.save();lineStyle(ctx,finish);ctx.globalAlpha=.35;ctx.beginPath();ctx.moveTo(70,610);ctx.lineTo(730,610);ctx.moveTo(80,250);ctx.lineTo(80,520);ctx.moveTo(720,250);ctx.lineTo(720,520);ctx.stroke();ctx.restore();}

function getSceneObjects(settings){
 const arr=deep(objects);
 if(!arr.some(o=>o.type==='ojika'))arr.push({type:'ojika',x:350,y:410,scale:1.35,auto:true});
 return arr;
}
function renderScenePass(ctx,settings,offsetX=0,offsetY=0,alpha=1){
 ctx.save();ctx.translate(offsetX,offsetY);ctx.globalAlpha=alpha;
 const text=settings.text;
 const hasDog=/犬|dog/.test(text);
 const hasLoop=/loop|ループ|電動.*(キック|スクーター|乗り物)|スクーター/.test(text);
 drawBackground(ctx,settings.finish);
 const sceneObjects=getSceneObjects(settings);
 const ojika=sceneObjects.find(o=>o.type==='ojika');
 sceneObjects.forEach(o=>{if(o.type==='ojika')drawOjikaFinal(ctx,o.x,o.y,o.scale||1,settings,hasLoop);else drawOtherFinal(ctx,o.x,o.y,o.scale||1,settings.finish);});
 if(ojika&&hasLoop)drawLoop(ctx,ojika.x+10,ojika.y+58,(ojika.scale||1)*1.05,settings.finish);
 if(ojika&&hasDog){const dx=Math.min(665,ojika.x+235),dy=Math.min(575,ojika.y+105);drawDog(ctx,dx,dy,1.05,settings.finish);drawLeash(ctx,ojika.x+40,ojika.y+18,dx+15,dy-15,settings.finish);}
 ctx.restore();
}
function renderMonochromeCleanup(){
 const settings=getSettings();white(octx,result);
 const source=document.createElement('canvas');source.width=800;source.height=800;const sx=source.getContext('2d');white(sx,source);sx.globalAlpha=.18;sx.drawImage(rough,0,0);octx.drawImage(source,0,0);
 if(settings.finish<35){const j=2+(35-settings.finish)/7;renderScenePass(octx,settings,-j,1,.28);renderScenePass(octx,settings,j,-1,.22);renderScenePass(octx,settings,0,0,.78);}
 else renderScenePass(octx,settings,0,0,1);
 octx.save();octx.strokeStyle='#111';octx.lineWidth=settings.finish>70?2:3;octx.strokeRect(18,18,764,764);octx.restore();
}
function compose(){renderMonochromeCleanup();}
function addHistory(label){historyItems.push({data:result.toDataURL('image/png'),label,time:new Date().toLocaleTimeString('ja-JP',{hour:'2-digit',minute:'2-digit'})});activeHistoryIndex=historyItems.length-1;renderHistory();}
function renderHistory(){const list=document.getElementById('historyList');list.innerHTML='';historyItems.forEach((item,index)=>{const div=document.createElement('div');div.className='historyItem'+(index===activeHistoryIndex?' active':'');const img=document.createElement('img');img.src=item.data;img.alt='差分 '+(index+1);const meta=document.createElement('div');meta.className='historyMeta';meta.textContent=(index+1)+'. '+item.label+' '+item.time;div.append(img,meta);div.onclick=()=>showHistory(index);list.appendChild(div);});list.scrollTop=list.scrollHeight;}
function showHistory(index){const item=historyItems[index];if(!item)return;const img=new Image();img.onload=()=>{white(octx,result);octx.drawImage(img,0,0);activeHistoryIndex=index;renderHistory();setStatus('差分 '+(index+1)+' を表示中。');};img.src=item.data;}

objectCanvas.addEventListener('pointerdown',start);objectCanvas.addEventListener('pointermove',move);objectCanvas.addEventListener('pointerup',end);objectCanvas.addEventListener('pointercancel',end);window.addEventListener('pointerup',end);
document.getElementById('penBtn').onclick=()=>{objectMode=null;erasing=false;setStatus('ペンモード');};
document.getElementById('eraserBtn').onclick=()=>{objectMode=null;erasing=true;setStatus('消しゴムモード');};
document.getElementById('ojikaObjBtn').onclick=()=>{objectMode='ojika';erasing=false;setStatus('キャンバスをタップして小鹿さんを配置。');};
document.getElementById('personObjBtn').onclick=()=>{objectMode='person';erasing=false;setStatus('キャンバスをタップして人物を配置。');};
document.getElementById('clearBtn').onclick=()=>{pushUndo();white(rctx,rough);objects=[];renderObjects();compose();setStatus('全消去しました。');};
document.getElementById('undoBtn').onclick=()=>{if(!undoStack.length)return;redoStack.push(snapshot());restore(undoStack.pop());setStatus('1つ戻しました。');};
document.getElementById('redoBtn').onclick=()=>{if(!redoStack.length)return;undoStack.push(snapshot());restore(redoStack.pop());setStatus('やり直しました。');};

const progressWrap=document.getElementById('progressWrap');
const progressBar=document.getElementById('progressBar');
const progressText=document.getElementById('progressText');
const progressTime=document.getElementById('progressTime');

function setProgress(p,label='描画中'){
 const v=Math.max(0,Math.min(100,Math.round(p)));
 progressWrap.classList.add('show');
 progressBar.style.width=v+'%';
 progressText.textContent=label+' '+v+'%';
}
function hideProgressSoon(){
 setTimeout(()=>{progressWrap.classList.remove('show');progressBar.style.width='0%';},380);
}
function fastRender(label,historyLabel){
 const start=performance.now();
 setProgress(4);
 requestAnimationFrame(()=>{
   setProgress(28);
   requestAnimationFrame(()=>{
     setProgress(62);
     compose();
     setProgress(92);
     requestAnimationFrame(()=>{
       addHistory(historyLabel);
       setProgress(100,'完了');
       const ms=Math.max(1,Math.round(performance.now()-start));
       progressTime.textContent=ms<1000?ms+'ms':(ms/1000).toFixed(1)+'秒';
       setStatus(label);
       hideProgressSoon();
     });
   });
 });
}

document.getElementById('generateBtn').onclick=()=>fastRender('完成絵を生成しました。','完成');
document.getElementById('reviseBtn').onclick=()=>fastRender('修正指示を反映しました。','修正');
document.getElementById('saveBtn').onclick=()=>{compose();const a=document.createElement('a');a.href=result.toDataURL('image/png');a.download='oshi-sketch.png';a.click();setStatus('PNGを書き出しました。');};

const finishRange=document.getElementById('finishRange');
const finishValue=document.getElementById('finishValue');
let lastFinishValueTap=0;
function updateFinishLabel(){const v=Number(finishRange.value);let label='基準';if(v<20)label='かなり雑';else if(v<40)label='やや雑';else if(v>80)label='かなり整う';else if(v>60)label='やや整う';finishValue.textContent=v+' / '+label;}
function resetFinishToCenter(){finishRange.value=50;updateFinishLabel();compose();setStatus('50 / 基準 に戻しました。');}
function handleFinishValueTap(){const now=Date.now();if(now-lastFinishValueTap<340){resetFinishToCenter();lastFinishValueTap=0;}else lastFinishValueTap=now;}
finishRange.addEventListener('input',()=>{updateFinishLabel();compose();});
finishValue.addEventListener('dblclick',resetFinishToCenter);finishValue.addEventListener('pointerup',handleFinishValueTap);
['description','cleanInstruction','revision'].forEach(id=>document.getElementById(id).addEventListener('input',compose));
['expressionPreset','hairPreset'].forEach(id=>document.getElementById(id).addEventListener('change',compose));

const dl=document.getElementById('downloadJsBtn');
if(dl)dl.onclick=async()=>{try{const res=await fetch('./app.js?'+Date.now(),{cache:'no-store'});const blob=new Blob([await res.text()],{type:'application/javascript'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='oshi-sketch-app.js';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){setStatus('JavaScriptのダウンロードに失敗しました。');}};

white(rctx,rough);white(octx,result);renderObjects();renderObjectIcons();updateFinishLabel();compose();