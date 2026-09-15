const fs=require('fs'),vm=require('vm');

const ops=[];
function makeCtx(){
  const fn=new Proxy({},{
    get(t,p){
      if(p in t)return t[p];
      if(['save','restore','fillRect','clearRect','drawImage','beginPath','arc','stroke','moveTo','lineTo','ellipse','fillText','quadraticCurveTo','fill','strokeRect','translate'].includes(p)){
        return (...args)=>{ops.push([p,...args]);};
      }
      return t[p];
    },
    set(t,p,v){t[p]=v;return true;}
  });
  return fn;
}
class El{
  constructor(id='',tag='div'){this.id=id;this.tagName=tag.toUpperCase();this.value='';this.textContent='';this.innerHTML='';this.children=[];this.listeners={};this.style={};this.className='';this.width=800;this.height=800;}
  addEventListener(n,fn){(this.listeners[n]??=[]).push(fn);}
  appendChild(x){this.children.push(x);return x;}
  append(...xs){this.children.push(...xs);}
  remove(){}
  click(){if(this.onclick)this.onclick({preventDefault(){}});}
  getContext(){return this._ctx??=(makeCtx());}
  toDataURL(){return 'data:image/png;base64,AAAA';}
  getBoundingClientRect(){return {left:0,top:0,width:800,height:800};}
}
const ids=['rough','objects','result','status','historyList','penBtn','eraserBtn','ojikaObjBtn','personObjBtn','clearBtn','undoBtn','redoBtn','generateBtn','reviseBtn','saveBtn','downloadJsBtn','finishRange','finishValue','expressionPreset','hairPreset','cleanInstruction','revision','description','ojikaIcon','personIcon'];
const els=Object.fromEntries(ids.map(id=>[id,new El(id,id.includes('Icon')||['rough','objects','result'].includes(id)?'canvas':'div')]));
els.finishRange.value='50';
els.expressionPreset.value='default';
els.hairPreset.value='promo';
els.description.value='小鹿なおさんがLOOPに乗って犬を散歩。虚無感マシマシ。';
els.cleanInstruction.value='';
els.revision.value='';

const document={
  getElementById:id=>els[id],
  createElement:tag=>new El('',tag),
  body:new El('body','body')
};
class Img extends El{set src(v){this._src=v;if(this.onload)this.onload();}get src(){return this._src;}}
global.document=document;
global.window={addEventListener(){}};
global.Image=Img;
global.URL={createObjectURL(){return 'blob:x';},revokeObjectURL(){}};
global.Blob=class{};
global.fetch=async()=>({text:async()=>''});
global.setTimeout=setTimeout;
global.clearTimeout=clearTimeout;

const src=fs.readFileSync('site/oshi-sketch/app.js','utf8');
vm.runInThisContext(src,{filename:'site/oshi-sketch/app.js'});

if(typeof els.generateBtn.onclick!=='function')throw new Error('generate button handler missing');
els.generateBtn.onclick();
if(els.status.textContent!=='完成絵を生成しました。')throw new Error('generate status mismatch: '+els.status.textContent);
if(els.historyList.children.length<1)throw new Error('history was not added');
if(ops.length<40)throw new Error('rendering operations unexpectedly low: '+ops.length);

els.finishRange.value='12';
els.finishValue.listeners.pointerup?.[0]();
els.finishValue.listeners.pointerup?.[0]();
if(String(els.finishRange.value)!=='50')throw new Error('double tap did not reset slider');

console.log('oshi-sketch smoke OK; ops='+ops.length);
