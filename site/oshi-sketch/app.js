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

function roughAmount(finish){return Math.max(.15,(100-finish)/22);}
function wiggle(seed,amount){return Math.sin(seed*12.9898+78.233)*amount;}
function handLine(ctx,x1,y1,x2,y2,finish,seed=1){
 const r=roughAmount(finish),passes=finish<35?3:2;
 ctx.save();ctx.strokeStyle='#111';ctx.lineCap='round';ctx.lineJoin='round';ctx.lineWidth=finish>75?1.8:2.2;
 for(let p=0;p<passes;p++){
  const a=r*(p+1)*.55;
  ctx.beginPath();
  ctx.moveTo(x1+wiggle(seed+p*11,a),y1+wiggle(seed+p*17,a));
  ctx.lineTo(x2+wiggle(seed+p*23,a),y2+wiggle(seed+p*29,a));
  ctx.stroke();
 }
 ctx.restore();
}
function handPoly(ctx,pts,finish,seed=1){
 for(let i=0;i<pts.length-1;i++)handLine(ctx,pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],finish,seed+i*7);
}
function handEllipse(ctx,x,y,rx,ry,finish,seed=1){
 const r=roughAmount(finish),passes=finish<35?3:2;
 ctx.save();ctx.strokeStyle='#111';ctx.fillStyle='#fff';ctx.lineWidth=finish>75?1.7:2.1;
 for(let p=0;p<passes;p++){
  const a=r*(p+1)*.42;
  ctx.beginPath();ctx.ellipse(x+wiggle(seed+p*13,a),y+wiggle(seed+p*19,a),Math.max(1,rx+wiggle(seed+p*31,a)),Math.max(1,ry+wiggle(seed+p*37,a)),wiggle(seed+p*41,.015),0,Math.PI*2);ctx.stroke();
 }
 ctx.restore();
}
function handCurve(ctx,x1,y1,cx,cy,x2,y2,finish,seed=1){
 const r=roughAmount(finish),passes=finish<35?3:2;
 ctx.save();ctx.strokeStyle='#111';ctx.lineWidth=finish>75?1.8:2.2;ctx.lineCap='round';
 for(let p=0;p<passes;p++){
  const a=r*(p+1)*.5;
  ctx.beginPath();
  ctx.moveTo(x1+wiggle(seed+p*3,a),y1+wiggle(seed+p*5,a));
  ctx.quadraticCurveTo(cx+wiggle(seed+p*7,a),cy+wiggle(seed+p*11,a),x2+wiggle(seed+p*13,a),y2+wiggle(seed+p*17,a));
  ctx.stroke();
 }
 ctx.restore();
}
function drawFaceFinal(ctx,x,y,s,exp,finish){
 const sw=s;
 if(exp==='void-max'){
  handLine(ctx,x-12*sw,y,x-4*sw,y,finish,401);
  handLine(ctx,x+4*sw,y,x+12*sw,y,finish,402);
  handLine(ctx,x-2*sw,y+13*sw,x+2*sw,y+13*sw,finish,403);
 }else if(exp==='void'){
  handLine(ctx,x-12*sw,y,x-5*sw,y+1*sw,finish,411);
  handLine(ctx,x+5*sw,y+1*sw,x+12*sw,y,finish,412);
  handLine(ctx,x-2*sw,y+12*sw,x+2*sw,y+12*sw,finish,413);
 }else if(exp==='smile'){
  handCurve(ctx,x-13*sw,y,x-9*sw,y+5*sw,x-5*sw,y,finish,421);
  handCurve(ctx,x+5*sw,y,x+9*sw,y+5*sw,x+13*sw,y,finish,422);
  handCurve(ctx,x-7*sw,y+9*sw,x,y+17*sw,x+7*sw,y+9*sw,finish,423);
 }else if(exp==='surprised'){
  handEllipse(ctx,x-9*sw,y,2.6*sw,3.3*sw,finish,431);
  handEllipse(ctx,x+9*sw,y,2.6*sw,3.3*sw,finish,432);
  handEllipse(ctx,x,y+13*sw,3.3*sw,4.3*sw,finish,433);
 }else{
  handEllipse(ctx,x-9*sw,y,2.2*sw,2.8*sw,finish,441);
  handEllipse(ctx,x+9*sw,y,2.2*sw,2.8*sw,finish,442);
  handLine(ctx,x-3*sw,y+12*sw,x+3*sw,y+12*sw,finish,443);
 }
}
function drawHairFinal(ctx,x,y,s,hair,finish){
 handCurve(ctx,x-27*s,y-3*s,x-17*s,y-34*s,x,y-34*s,finish,501);
 handCurve(ctx,x,y-34*s,x+19*s,y-34*s,x+27*s,y-3*s,finish,502);
 handCurve(ctx,x-27*s,y-3*s,x-30*s,y+20*s,x-27*s,y+43*s,finish,503);
 handCurve(ctx,x+27*s,y-3*s,x+30*s,y+20*s,x+27*s,y+43*s,finish,504);
 handCurve(ctx,x-19*s,y-17*s,x-8*s,y-7*s,x-3*s,y-20*s,finish,505);
 handCurve(ctx,x-1*s,y-21*s,x+8*s,y-8*s,x+18*s,y-17*s,finish,506);
 if(hair==='twin'){
  handCurve(ctx,x-25*s,y-5*s,x-50*s,y+2*s,x-42*s,y+28*s,finish,507);
  handCurve(ctx,x+25*s,y-5*s,x+50*s,y+2*s,x+42*s,y+28*s,finish,508);
 }else if(hair==='pony'){
  handCurve(ctx,x+25*s,y-5*s,x+58*s,y+8*s,x+38*s,y+46*s,finish,509);
 }else if(hair==='half'){
  handCurve(ctx,x-15*s,y-28*s,x,y-39*s,x+15*s,y-28*s,finish,510);
 }
}
function drawOjikaFinal(ctx,x,y,s,settings,onLoop){
 const f=settings.finish,headY=y-78*s;
 handEllipse(ctx,x,headY,27*s,31*s,f,600);
 drawHairFinal(ctx,x,headY,s,settings.hair,f);
 drawFaceFinal(ctx,x,headY+4*s,s,settings.expression,f);

 // neck + shoulders + torso: adult human proportions rather than stick figure
 handLine(ctx,x-8*s,headY+29*s,x-8*s,y-39*s,f,610);
 handLine(ctx,x+8*s,headY+29*s,x+8*s,y-39*s,f,611);
 handCurve(ctx,x-8*s,y-39*s,x-36*s,y-30*s,x-43*s,y-4*s,f,612);
 handCurve(ctx,x+8*s,y-39*s,x+36*s,y-30*s,x+43*s,y-4*s,f,613);
 handCurve(ctx,x-43*s,y-4*s,x-38*s,y+42*s,x-26*s,y+74*s,f,614);
 handCurve(ctx,x+43*s,y-4*s,x+38*s,y+42*s,x+26*s,y+74*s,f,615);
 handLine(ctx,x-26*s,y+74*s,x+26*s,y+74*s,f,616);

 if(onLoop){
  // arms naturally reaching the handle
  handCurve(ctx,x-34*s,y-20*s,x-48*s,y+4*s,x-35*s,y+26*s,f,620);
  handCurve(ctx,x-35*s,y+26*s,x-10*s,y+12*s,x+18*s,y+4*s,f,621);
  handCurve(ctx,x+34*s,y-20*s,x+50*s,y+2*s,x+38*s,y+24*s,f,622);
  handCurve(ctx,x+38*s,y+24*s,x+28*s,y+10*s,x+18*s,y+4*s,f,623);
  // legs standing on deck
  handCurve(ctx,x-15*s,y+74*s,x-20*s,y+106*s,x-17*s,y+139*s,f,624);
  handCurve(ctx,x+15*s,y+74*s,x+20*s,y+106*s,x+17*s,y+139*s,f,625);
  handLine(ctx,x-27*s,y+141*s,x-8*s,y+141*s,f,626);
  handLine(ctx,x+8*s,y+141*s,x+27*s,y+141*s,f,627);
 }else{
  handCurve(ctx,x-34*s,y-20*s,x-48*s,y+15*s,x-30*s,y+45*s,f,628);
  handCurve(ctx,x+34*s,y-20*s,x+48*s,y+15*s,x+30*s,y+45*s,f,629);
  handCurve(ctx,x-14*s,y+74*s,x-19*s,y+113*s,x-20*s,y+153*s,f,630);
  handCurve(ctx,x+14*s,y+74*s,x+19*s,y+113*s,x+20*s,y+153*s,f,631);
 }
 if(settings.expression==='void-max'){
  ctx.save();ctx.fillStyle='#111';ctx.font=Math.max(18,20*s)+'px sans-serif';ctx.textAlign='center';ctx.fillText('……',x+74*s,headY-8*s);ctx.restore();
 }
}
function drawOtherFinal(ctx,x,y,s,finish){
 const hy=y-62*s;handEllipse(ctx,x,hy,25*s,29*s,finish,700);handEllipse(ctx,x-8*s,hy+3*s,2*s,2*s,finish,701);handEllipse(ctx,x+8*s,hy+3*s,2*s,2*s,finish,702);
 handLine(ctx,x,hy+29*s,x,y+67*s,finish,703);handLine(ctx,x,y-10*s,x-33*s,y+20*s,finish,704);handLine(ctx,x,y-10*s,x+33*s,y+20*s,finish,705);handLine(ctx,x,y+67*s,x-22*s,y+127*s,finish,706);handLine(ctx,x,y+67*s,x+22*s,y+127*s,finish,707);
}
function drawLoop(ctx,x,y,s,finish){
 // compact standing mobility/scooter device
 handEllipse(ctx,x-35*s,y+64*s,17*s,17*s,finish,801);
 handEllipse(ctx,x+47*s,y+64*s,17*s,17*s,finish,802);
 handPoly(ctx,[[x-38*s,y+45*s],[x+31*s,y+45*s],[x+50*s,y+54*s]],finish,803);
 handLine(ctx,x+20*s,y+45*s,x+7*s,y-58*s,finish,804);
 handLine(ctx,x+7*s,y-58*s,x+42*s,y-58*s,finish,805);
 handLine(ctx,x+7*s,y-58*s,x-14*s,y-58*s,finish,806);
 handLine(ctx,x-25*s,y+40*s,x+26*s,y+40*s,finish,807);
}
function drawDog(ctx,x,y,s,finish){
 // intentionally simple but recognisably hand-drawn dog
 handEllipse(ctx,x,y,38*s,24*s,finish,901);
 handEllipse(ctx,x+43*s,y-20*s,20*s,19*s,finish,902);
 handCurve(ctx,x+31*s,y-32*s,x+22*s,y-51*s,x+39*s,y-39*s,finish,903);
 handCurve(ctx,x+52*s,y-32*s,x+61*s,y-51*s,x+61*s,y-30*s,finish,904);
 handCurve(ctx,x+53*s,y-16*s,x+70*s,y-12*s,x+66*s,y-5*s,finish,905);
 handEllipse(ctx,x+48*s,y-23*s,2*s,2*s,finish,906);
 handEllipse(ctx,x+66*s,y-7*s,2.6*s,2.2*s,finish,907);
 handCurve(ctx,x-35*s,y-7*s,x-60*s,y-29*s,x-51*s,y-49*s,finish,908);
 handCurve(ctx,x-23*s,y+18*s,x-28*s,y+41*s,x-27*s,y+58*s,finish,909);
 handCurve(ctx,x+5*s,y+20*s,x+7*s,y+43*s,x+7*s,y+59*s,finish,910);
 handCurve(ctx,x+23*s,y+17*s,x+30*s,y+42*s,x+31*s,y+56*s,finish,911);
 // harness
 handCurve(ctx,x-6*s,y-21*s,x+2*s,y,x+7*s,y+21*s,finish,912);
 handLine(ctx,x-12*s,y-13*s,x+19*s,y-10*s,finish,913);
}
function drawLeash(ctx,x1,y1,x2,y2,finish){handCurve(ctx,x1,y1,(x1+x2)/2,y1+42,x2,y2,finish,980);}
function drawBackground(ctx,finish,text){
 const f=finish;
 // promenade / river rail, kept light but visible
 const old=octx.globalAlpha;octx.globalAlpha=.62;
 handLine(ctx,55,615,745,615,f,1001);
 handLine(ctx,70,320,730,320,f,1002);
 handLine(ctx,70,352,730,352,f,1003);
 for(let x=80;x<=720;x+=80)handLine(ctx,x,320,x,520,f,1010+x);
 handLine(ctx,70,520,730,520,f,1020);
 // sparse skyline
 handPoly(ctx,[[80,285],[80,245],[135,245],[135,275],[175,275],[175,220],[225,220],[225,282]],f,1030);
 handPoly(ctx,[[560,280],[560,235],[615,235],[615,260],[655,260],[655,210],[715,210],[715,282]],f,1040);
 if(/公園|park/.test(text)){handCurve(ctx,250,305,270,250,290,305,f,1050);handCurve(ctx,268,270,245,248,228,275,f,1051);}
 octx.globalAlpha=old;
}
function getSceneObjects(settings){
 const arr=deep(objects);
 if(!arr.some(o=>o.type==='ojika'))arr.push({type:'ojika',x:345,y:390,scale:1.25,auto:true});
 return arr;
}
function renderScenePass(ctx,settings){
 const text=settings.text;
 const hasDog=/犬|dog/.test(text);
 const hasLoop=/loop|ループ|電動.*(キック|スクーター|乗り物)|スクーター/.test(text);
 drawBackground(ctx,settings.finish,text);
 const sceneObjects=getSceneObjects(settings);
 const ojika=sceneObjects.find(o=>o.type==='ojika');
 sceneObjects.forEach(o=>{if(o.type==='ojika')drawOjikaFinal(ctx,o.x,o.y,o.scale||1,settings,hasLoop);else drawOtherFinal(ctx,o.x,o.y,o.scale||1,settings.finish);});
 if(ojika&&hasLoop)drawLoop(ctx,ojika.x+7,ojika.y+98,(ojika.scale||1),settings.finish);
 if(ojika&&hasDog){
  const dx=Math.min(650,ojika.x+245),dy=Math.min(565,ojika.y+124);
  drawDog(ctx,dx,dy,1.05,settings.finish);
  drawLeash(ctx,ojika.x+38*(ojika.scale||1),ojika.y+12,dx+12,dy-22,settings.finish);
 }
}
function renderMonochromeCleanup(){
 const settings=getSettings();
 white(octx,result);
 // The source rough is layout input only. It is deliberately NOT copied into the finished image.
 renderScenePass(octx,settings);
 octx.save();octx.strokeStyle='#111';octx.lineWidth=2;octx.strokeRect(18,18,764,764);octx.restore();
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