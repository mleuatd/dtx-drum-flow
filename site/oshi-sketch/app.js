const rough=document.getElementById('rough');
const rctx=rough.getContext('2d');
const objectCanvas=document.getElementById('objects');
const objctx=objectCanvas.getContext('2d');
const result=document.getElementById('result');
const octx=result.getContext('2d');
let drawing=false, erasing=false, last=null;
let undoStack=[], redoStack=[];
let historyItems=[];
let activeHistoryIndex=-1;
let objectMode=null;
let objects=[];
let pressTimer=null;
let pressedObjectIndex=-1;
let draggingObjectIndex=-1;
let pressStart=null;
const LONG_PRESS_MS=420;

function white(ctx,canvas){ctx.save();ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.restore()}
white(rctx,rough); white(octx,result); renderObjects();

function snapshot(){
 return {rough:rough.toDataURL(),objects:JSON.parse(JSON.stringify(objects))}
}
function pushUndo(){undoStack.push(snapshot()); if(undoStack.length>30)undoStack.shift(); redoStack=[]}
function restore(state){
 const img=new Image();
 img.onload=()=>{rctx.clearRect(0,0,rough.width,rough.height);rctx.drawImage(img,0,0)};
 img.src=state.rough;
 objects=JSON.parse(JSON.stringify(state.objects||[]));
 renderObjects();
}
function pos(e){
 const rect=objectCanvas.getBoundingClientRect();
 const p=e.touches?e.touches[0]:e;
 return {x:(p.clientX-rect.left)*objectCanvas.width/rect.width,y:(p.clientY-rect.top)*objectCanvas.height/rect.height};
}
function hitObject(x,y){
 for(let i=objects.length-1;i>=0;i--){
   const o=objects[i],dx=x-o.x,dy=y-o.y;
   if(Math.hypot(dx,dy)<90*(o.scale||1)) return i;
 }
 return -1;
}
function start(e){
 e.preventDefault();
 const p=pos(e);
 if(objectMode){
   pushUndo();
   objects.push({type:objectMode,x:p.x,y:p.y,scale:1});
   renderObjects();
   setStatus(objectMode==='ojika'?'小鹿さんマークを別レイヤーに配置しました。':'人物マークを別レイヤーに配置しました。');
   objectMode=null;
   return;
 }
 const hit=hitObject(p.x,p.y);
 if(hit>=0){
   pressedObjectIndex=hit;
   pressStart=p;
   pressTimer=setTimeout(()=>{
     pushUndo();
     draggingObjectIndex=pressedObjectIndex;
     renderObjects();
     setStatus('長押しで選択しました。薄く表示しているオブジェクトを移動できます。');
   },LONG_PRESS_MS);
   return;
 }
 pushUndo();drawing=true;last=p
}
function move(e){
 const p=pos(e);
 if(draggingObjectIndex>=0){
   e.preventDefault();
   objects[draggingObjectIndex].x=p.x;
   objects[draggingObjectIndex].y=p.y;
   renderObjects();
   return;
 }
 if(pressTimer&&pressStart&&Math.hypot(p.x-pressStart.x,p.y-pressStart.y)>18){
   clearTimeout(pressTimer);pressTimer=null;pressedObjectIndex=-1;
 }
 if(!drawing)return;e.preventDefault();
 rctx.save();rctx.lineCap='round';rctx.lineJoin='round';
 rctx.lineWidth=erasing?28:5;rctx.strokeStyle=erasing?'#fff':'#111';
 rctx.beginPath();rctx.moveTo(last.x,last.y);rctx.lineTo(p.x,p.y);rctx.stroke();rctx.restore();last=p;
}
function end(){
 if(pressTimer){clearTimeout(pressTimer);pressTimer=null}
 if(draggingObjectIndex>=0){
   setStatus('オブジェクトの移動を確定しました。');
   draggingObjectIndex=-1;pressedObjectIndex=-1;pressStart=null;renderObjects();
 }
 drawing=false;last=null
}
function drawPerson(ctx,x,y,scale){
 ctx.save();ctx.strokeStyle='#111';ctx.fillStyle='#111';ctx.lineWidth=7*scale;ctx.lineCap='round';
 ctx.beginPath();ctx.arc(x,y-45*scale,24*scale,0,Math.PI*2);ctx.stroke();
 ctx.beginPath();ctx.moveTo(x,y-20*scale);ctx.lineTo(x,y+40*scale);
 ctx.moveTo(x,y);ctx.lineTo(x-32*scale,y+20*scale);ctx.moveTo(x,y);ctx.lineTo(x+32*scale,y+20*scale);
 ctx.moveTo(x,y+40*scale);ctx.lineTo(x-26*scale,y+82*scale);ctx.moveTo(x,y+40*scale);ctx.lineTo(x+26*scale,y+82*scale);ctx.stroke();
 ctx.restore();
}
function renderObjects(){
 objctx.clearRect(0,0,objectCanvas.width,objectCanvas.height);
 objects.forEach((o,i)=>{
   objctx.save();
   if(i===draggingObjectIndex) objctx.globalAlpha=.42;
   if(o.type==='ojika') drawOjika(objctx,o.x,o.y,o.scale||1);
   else drawPerson(objctx,o.x,o.y,o.scale||1);
   objctx.restore();
 });
}
function drawOjika(ctx,x,y,scale){
 ctx.save();ctx.strokeStyle='#111';ctx.fillStyle='#fff';ctx.lineWidth=5*scale;ctx.lineCap='round';
 const cy=y-45*scale,r=23*scale;
 for(let i=0;i<12;i++){const a=i*Math.PI/6,px=x+Math.cos(a)*36*scale,py=cy+Math.sin(a)*36*scale;
   ctx.beginPath();ctx.ellipse(px,py,10*scale,18*scale,a,0,Math.PI*2);ctx.stroke();}
 ctx.beginPath();ctx.arc(x,cy,r,0,Math.PI*2);ctx.fill();ctx.stroke();
 ctx.fillStyle='#111';ctx.font=(18*scale)+'px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('小鹿',x,cy);
 ctx.beginPath();ctx.moveTo(x,y-20*scale);ctx.lineTo(x,y+40*scale);
 ctx.moveTo(x,y);ctx.lineTo(x-32*scale,y+20*scale);ctx.moveTo(x,y);ctx.lineTo(x+32*scale,y+20*scale);
 ctx.moveTo(x,y+40*scale);ctx.lineTo(x-26*scale,y+82*scale);ctx.moveTo(x,y+40*scale);ctx.lineTo(x+26*scale,y+82*scale);ctx.stroke();
 ctx.restore();
}
function renderObjectIcons(){
 const a=document.getElementById('ojikaIcon'),ac=a.getContext('2d');white(ac,a);drawOjika(ac,a.width/2,82,.55);
 const b=document.getElementById('personIcon'),bc=b.getContext('2d');white(bc,b);drawPerson(bc,b.width/2,82,.55);
}
objectCanvas.addEventListener('pointerdown',start);
objectCanvas.addEventListener('pointermove',move);
objectCanvas.addEventListener('pointerup',end);
objectCanvas.addEventListener('pointercancel',end);
window.addEventListener('pointerup',end);
document.getElementById('penBtn').onclick=()=>{objectMode=null;erasing=false;setStatus('ペンモード')};
document.getElementById('ojikaObjBtn').onclick=()=>{objectMode='ojika';erasing=false;setStatus('キャンバスをタップすると小鹿さんマークを配置します。')};
document.getElementById('personObjBtn').onclick=()=>{objectMode='person';erasing=false;setStatus('キャンバスをタップすると人物マークを配置します。')};
document.getElementById('eraserBtn').onclick=()=>{erasing=true;setStatus('消しゴムモード')};
document.getElementById('clearBtn').onclick=()=>{pushUndo();white(rctx,rough);objects=[];renderObjects();setStatus('ラフとオブジェクトを全消去しました')};
document.getElementById('undoBtn').onclick=()=>{
 if(!undoStack.length)return;redoStack.push(snapshot());restore(undoStack.pop());setStatus('1つ戻しました')
};
document.getElementById('redoBtn').onclick=()=>{
 if(!redoStack.length)return;undoStack.push(snapshot());restore(redoStack.pop());setStatus('やり直しました')
};

function setStatus(s){document.getElementById('status').textContent=s}

function addHistory(label){
 const data=result.toDataURL('image/png');
 historyItems.push({data,label,time:new Date().toLocaleTimeString('ja-JP',{hour:'2-digit',minute:'2-digit'})});
 activeHistoryIndex=historyItems.length-1;
 renderHistory();
}
function renderHistory(){
 const list=document.getElementById('historyList');
 list.innerHTML='';
 historyItems.forEach((item,index)=>{
   const div=document.createElement('div');
   div.className='historyItem'+(index===activeHistoryIndex?' active':'');
   div.title='クリックするとこの差分を再表示';
   const img=document.createElement('img');
   img.src=item.data;
   img.alt='差分 '+(index+1);
   const meta=document.createElement('div');
   meta.className='historyMeta';
   meta.textContent=(index+1)+'. '+item.label+' '+item.time;
   div.append(img,meta);
   div.onclick=()=>showHistory(index);
   list.appendChild(div);
 });
 list.scrollTop=list.scrollHeight;
}
function showHistory(index){
 const item=historyItems[index];
 if(!item)return;
 const img=new Image();
 img.onload=()=>{
   white(octx,result);
   octx.drawImage(img,0,0,result.width,result.height);
   activeHistoryIndex=index;
   renderHistory();
   setStatus('差分 '+(index+1)+' を再表示しています。');
 };
 img.src=item.data;
}

function getCleanSettings(){
 return {
   finish:Number(document.getElementById('finishRange').value),
   expression:document.getElementById('expressionPreset').value,
   hair:document.getElementById('hairPreset').value,
   instruction:document.getElementById('cleanInstruction').value.trim()
 };
}
function mergedSourceCanvas(){
 const t=document.createElement('canvas');t.width=800;t.height=800;
 const x=t.getContext('2d');white(x,t);x.drawImage(rough,0,0);
 return t;
}
function cleanLine(ctx,finish){
 ctx.strokeStyle='#111';ctx.fillStyle='#111';ctx.lineCap='round';ctx.lineJoin='round';
 ctx.lineWidth=finish<35?3:finish>70?2:2.5;
}
function drawCleanPerson(ctx,o,finish){
 const s=o.scale||1,x=o.x,y=o.y;
 ctx.save();cleanLine(ctx,finish);
 ctx.beginPath();ctx.arc(x,y-46*s,24*s,0,Math.PI*2);ctx.stroke();
 ctx.beginPath();ctx.moveTo(x,y-20*s);ctx.lineTo(x,y+40*s);
 ctx.moveTo(x,y);ctx.lineTo(x-30*s,y+18*s);ctx.moveTo(x,y);ctx.lineTo(x+30*s,y+18*s);
 ctx.moveTo(x,y+40*s);ctx.lineTo(x-24*s,y+80*s);ctx.moveTo(x,y+40*s);ctx.lineTo(x+24*s,y+80*s);ctx.stroke();
 ctx.restore();
}
function drawCleanOjika(ctx,o,settings){
 const s=o.scale||1,x=o.x,y=o.y,finish=settings.finish;
 ctx.save();cleanLine(ctx,finish);
 const headY=y-48*s,headR=28*s;
 ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(x,headY,headR,0,Math.PI*2);ctx.fill();ctx.stroke();

 // hair silhouette
 ctx.beginPath();
 if(settings.hair==='twin'){
   ctx.arc(x,headY-2*s,30*s,Math.PI*.95,Math.PI*2.05);
   ctx.moveTo(x-24*s,headY-10*s);ctx.quadraticCurveTo(x-48*s,headY,x-38*s,headY+26*s);
   ctx.moveTo(x+24*s,headY-10*s);ctx.quadraticCurveTo(x+48*s,headY,x+38*s,headY+26*s);
 }else if(settings.hair==='pony'){
   ctx.arc(x,headY-2*s,30*s,Math.PI*.95,Math.PI*2.05);
   ctx.moveTo(x+24*s,headY-6*s);ctx.quadraticCurveTo(x+55*s,headY+12*s,x+34*s,headY+42*s);
 }else if(settings.hair==='half'){
   ctx.arc(x,headY-2*s,30*s,Math.PI*.95,Math.PI*2.05);
   ctx.moveTo(x-22*s,headY+2*s);ctx.lineTo(x-26*s,headY+38*s);
   ctx.moveTo(x+22*s,headY+2*s);ctx.lineTo(x+26*s,headY+38*s);
 }else{
   ctx.arc(x,headY-2*s,30*s,Math.PI*.95,Math.PI*2.05);
   ctx.moveTo(x-24*s,headY);ctx.lineTo(x-28*s,headY+42*s);
   ctx.moveTo(x+24*s,headY);ctx.lineTo(x+28*s,headY+42*s);
 }
 ctx.stroke();

 // bangs
 ctx.beginPath();
 ctx.moveTo(x-20*s,headY-18*s);ctx.quadraticCurveTo(x-8*s,headY-8*s,x-4*s,headY-20*s);
 ctx.moveTo(x-2*s,headY-20*s);ctx.quadraticCurveTo(x+8*s,headY-8*s,x+18*s,headY-17*s);ctx.stroke();

 // expression
 ctx.beginPath();
 if(settings.expression==='void-max'){
   ctx.moveTo(x-14*s,headY);ctx.lineTo(x-5*s,headY);
   ctx.moveTo(x+5*s,headY);ctx.lineTo(x+14*s,headY);
   ctx.moveTo(x-2*s,headY+13*s);ctx.lineTo(x+2*s,headY+13*s);
 }else if(settings.expression==='void'){
   ctx.moveTo(x-13*s,headY);ctx.lineTo(x-6*s,headY+1*s);
   ctx.moveTo(x+6*s,headY+1*s);ctx.lineTo(x+13*s,headY);
   ctx.moveTo(x-2*s,headY+12*s);ctx.lineTo(x+2*s,headY+12*s);
 }else if(settings.expression==='smile'){
   ctx.arc(x-9*s,headY,5*s,0,Math.PI);
   ctx.arc(x+9*s,headY,5*s,0,Math.PI);
   ctx.arc(x,headY+8*s,7*s,0,Math.PI);
 }else if(settings.expression==='surprised'){
   ctx.arc(x-9*s,headY,3*s,0,Math.PI*2);
   ctx.arc(x+9*s,headY,3*s,0,Math.PI*2);
   ctx.arc(x,headY+12*s,3*s,0,Math.PI*2);
 }else{
   ctx.arc(x-9*s,headY,2.5*s,0,Math.PI*2);
   ctx.arc(x+9*s,headY,2.5*s,0,Math.PI*2);
   ctx.moveTo(x-3*s,headY+12*s);ctx.lineTo(x+3*s,headY+12*s);
 }
 ctx.stroke();

 // simplified human body
 ctx.beginPath();
 ctx.moveTo(x,headY+headR);ctx.lineTo(x,y+38*s);
 ctx.moveTo(x,y-2*s);ctx.lineTo(x-28*s,y+22*s);ctx.moveTo(x,y-2*s);ctx.lineTo(x+28*s,y+22*s);
 ctx.moveTo(x,y+38*s);ctx.lineTo(x-22*s,y+80*s);ctx.moveTo(x,y+38*s);ctx.lineTo(x+22*s,y+80*s);ctx.stroke();
 ctx.restore();
}
function renderMonochromeCleanup(){
 const s=getCleanSettings();
 const src=mergedSourceCanvas();
 white(octx,result);

 if(s.finish<34){
   const strength=(34-s.finish)/34;
   const jitter=2+strength*4;
   octx.globalAlpha=.55;
   octx.drawImage(src,-jitter,1);
   octx.globalAlpha=.35;
   octx.drawImage(src,jitter,-1);
   octx.globalAlpha=.75;
   octx.drawImage(src,0,0);
   octx.globalAlpha=1;
 }else if(s.finish<=66){
   octx.drawImage(src,0,0);
 }else{
   const tmp=document.createElement('canvas');tmp.width=800;tmp.height=800;
   const tx=tmp.getContext('2d');
   tx.filter='grayscale(1) blur('+(0.25+((s.finish-66)/34)*0.65)+'px) contrast('+(1.3+((s.finish-66)/34)*.9)+')';
   tx.drawImage(src,0,0);
   const im=tx.getImageData(0,0,800,800),d=im.data;
   const threshold=205-((s.finish-66)/34)*35;
   for(let i=0;i<d.length;i+=4){
     const v=(d[i]+d[i+1]+d[i+2])/3;
     const out=v<threshold?0:255;
     d[i]=d[i+1]=d[i+2]=out;d[i+3]=255;
   }
   tx.putImageData(im,0,0);
   octx.drawImage(tmp,0,0);
 }

 octx.save();
 octx.strokeStyle='#111';
 octx.lineWidth=s.finish<34?2:3;
 octx.strokeRect(18,18,result.width-36,result.height-36);

 const desc=document.getElementById('description').value.trim();
 const rev=document.getElementById('revision').value.trim();
 const expMap={default:'デフォルト',void:'虚無','void-max':'虚無感マシマシ',smile:'笑顔',surprised:'驚き',custom:'自由指定'};
 const hairMap={promo:'宣材写真イメージ',twin:'ツインテール',pony:'ひとつ結び',half:'ハーフアップ',custom:'自由指定'};
 const note=[desc,rev?('修正: '+rev):'',s.instruction?('清書: '+s.instruction):''].filter(Boolean).join(' / ');

 octx.fillStyle='rgba(255,255,255,.94)';
 octx.fillRect(28,result.height-166,result.width-56,130);
 octx.fillStyle='#111';octx.font='20px sans-serif';
 wrapText(octx,note,44,result.height-126,result.width-88,27,3);
 octx.font='16px sans-serif';
 octx.fillText('表情: '+expMap[s.expression]+'　髪型: '+hairMap[s.hair]+'　整い具合: '+s.finish,44,result.height-48);
 octx.restore();
}
function compose(extra=''){
 renderMonochromeCleanup();
}
function wrapText(ctx,text,x,y,maxWidth,lineHeight,maxLines){
 const chars=[...text];let line='',lines=[];
 for(const ch of chars){
   const test=line+ch;if(ctx.measureText(test).width>maxWidth&&line){lines.push(line);line=ch}else line=test;
   if(lines.length>=maxLines-1)break;
 }
 if(lines.length<maxLines&&line)lines.push(line);
 lines.forEach((l,i)=>ctx.fillText(l,x,y+i*lineHeight));
}
document.getElementById('generateBtn').onclick=()=>{compose();addHistory('清書');setStatus('白黒・手描き基準で清書しました。中央50が現在の基準です。')};
document.getElementById('reviseBtn').onclick=()=>{compose();addHistory('修正');setStatus('修正設定を反映して差分履歴へ追加しました。')};
renderObjectIcons();
const finishRange=document.getElementById('finishRange');
const finishValue=document.getElementById('finishValue');
const expressionPreset=document.getElementById('expressionPreset');
const hairPreset=document.getElementById('hairPreset');
const cleanInstruction=document.getElementById('cleanInstruction');
const revisionBox=document.getElementById('revision');
let lastFinishValueTap=0;

function resetFinishToCenter(){
 finishRange.value=50;
 updateFinishLabel();
 compose();
 setStatus('線の整い具合を 50 / 基準 に戻しました。');
}

function handleFinishValueTap(){
 const now=Date.now();
 if(now-lastFinishValueTap<320){
   resetFinishToCenter();
   lastFinishValueTap=0;
 }else{
   lastFinishValueTap=now;
 }
}

function updateFinishLabel(){
 const v=Number(finishRange.value);
 let label='基準';
 if(v<20)label='かなり雑';
 else if(v<40)label='やや雑';
 else if(v>80)label='かなり整う';
 else if(v>60)label='やや整う';
 document.getElementById('finishValue').textContent=v+' / '+label;
}
finishRange.addEventListener('input',()=>{updateFinishLabel();compose();});
finishValue.addEventListener('dblclick',resetFinishToCenter);
finishValue.addEventListener('pointerup',handleFinishValueTap);
expressionPreset.addEventListener('change',compose);
hairPreset.addEventListener('change',compose);
cleanInstruction.addEventListener('input',compose);
revisionBox.addEventListener('input',compose);
updateFinishLabel();
document.getElementById('saveBtn').onclick=()=>{
 compose();
 const a=document.createElement('a');a.href=result.toDataURL('image/png');a.download='oshi-sketch.png';a.click();
 setStatus('PNGを書き出しました。');
};
