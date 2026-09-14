const GM_DRUM_MAP={35:"BD",36:"BD",37:"SN",38:"SN",39:"SN",40:"SN",41:"FT",43:"FT",45:"LT",47:"LT",48:"HT",50:"HT",42:"HH",44:"HH",46:"HH",49:"RC",52:"RC",55:"RC",57:"RC",51:"RD",53:"RD",59:"RD"};
const DTX_MAP={LC:"LC",HH:"HH",SD:"SN",SN:"SN",HT:"HT",LT:"LT",FT:"FT",CY:"RC",RC:"RC",RD:"RD",LP:"LP",LB:"LB",BD:"BD"};

export function makeSample(){
  const bpm=120,duration=13,notes=[];
  for(let beat=0;beat<26;beat++){
    const t=beat*.5;
    notes.push({time:t,part:"HH",velocity:.68});
    if(beat%2===0)notes.push({time:t,part:"BD",velocity:.9});
    else notes.push({time:t,part:"SN",velocity:.85});
    if(beat%4===3)notes.push({time:t+.25,part:"HH",velocity:.58});
  }
  return {name:"8ビート練習サンプル",bpm,duration,notes:notes.slice(0,87)};
}

export async function parseChart(file){
  const ext=file.name.split(".").pop().toLowerCase();
  if(ext==="mid"||ext==="midi") return parseMidi(await file.arrayBuffer(),file.name);
  if(ext==="dtx"||ext==="gda") return parseTextChart(await file.text(),file.name);
  throw new Error("対応していない譜面形式です");
}

function parseMidi(buf,name){
  const dv=new DataView(buf); let p=0;
  const str=n=>{let s="";for(let i=0;i<n;i++)s+=String.fromCharCode(dv.getUint8(p++));return s};
  const u32=()=>{const v=dv.getUint32(p);p+=4;return v}; const u16=()=>{const v=dv.getUint16(p);p+=2;return v};
  const varlen=()=>{let v=0,b;do{b=dv.getUint8(p++);v=(v<<7)|(b&127)}while(b&128);return v};
  if(str(4)!=="MThd")throw new Error("MIDIヘッダが不正です");
  const hlen=u32(),format=u16(),tracks=u16(),division=u16();p=8+hlen;
  if(division&0x8000)throw new Error("SMPTE time divisionは未対応です");
  const events=[],tempos=[{tick:0,usPerQ:500000}];
  for(let ti=0;ti<tracks;ti++){
    if(str(4)!=="MTrk")throw new Error("MIDIトラックが不正です");
    const len=u32(),end=p+len;let tick=0,running=0;
    while(p<end){
      tick+=varlen(); let st=dv.getUint8(p++);
      if(st<0x80){p--;st=running}else running=st;
      if(st===0xff){
        const type=dv.getUint8(p++),l=varlen();
        if(type===0x51&&l===3){const us=(dv.getUint8(p)<<16)|(dv.getUint8(p+1)<<8)|dv.getUint8(p+2);tempos.push({tick,usPerQ:us})}
        p+=l;continue;
      }
      if(st===0xf0||st===0xf7){p+=varlen();continue}
      const cmd=st&0xf0,ch=st&15;
      if(cmd===0x80||cmd===0x90){const note=dv.getUint8(p++),vel=dv.getUint8(p++);if(cmd===0x90&&vel&&ch===9&&GM_DRUM_MAP[note])events.push({tick,part:GM_DRUM_MAP[note],velocity:vel/127})}
      else if(cmd===0xa0||cmd===0xb0||cmd===0xe0)p+=2; else if(cmd===0xc0||cmd===0xd0)p+=1; else break;
    }p=end;
  }
  tempos.sort((a,b)=>a.tick-b.tick);events.sort((a,b)=>a.tick-b.tick);
  const tickToSec=t=>{let sec=0,lastTick=0,us=tempos[0].usPerQ;for(let i=1;i<tempos.length&&tempos[i].tick<t;i++){sec+=(tempos[i].tick-lastTick)*us/division/1e6;lastTick=tempos[i].tick;us=tempos[i].usPerQ}return sec+(t-lastTick)*us/division/1e6};
  const notes=events.map(e=>({...e,time:tickToSec(e.tick)}));
  const bpm=Math.round(60000000/tempos[0].usPerQ),duration=(notes.at(-1)?.time||0)+2;
  return {name,bpm,duration,notes};
}

function parseTextChart(text,name){
  let bpm=120;const measures=new Map();const lines=text.replace(/\r/g,"").split("\n");
  for(const raw of lines){const line=raw.trim();let m;
    if((m=line.match(/^#BPM\s*[: ]\s*([0-9.]+)/i)))bpm=Number(m[1])||bpm;
    if((m=line.match(/^#(\d{3})([0-9A-Z]{2})\s*:\s*([0-9A-Z]+)/i))){const measure=Number(m[1]),channel=m[2].toUpperCase(),data=m[3].toUpperCase();if(!measures.has(measure))measures.set(measure,[]);measures.get(measure).push({channel,data})}
  }
  const channelMap={11:"HH",12:"SN",13:"BD",14:"HT",15:"LT",16:"RC",17:"FT",18:"LC",19:"RD",1A:"LP",1B:"LB",HH:"HH",SD:"SN",BD:"BD",HT:"HT",LT:"LT",FT:"FT",CY:"RC",RD:"RD"};
  const secPerMeasure=240/bpm,notes=[];
  for(const [measure,rows] of measures)for(const r of rows){const part=channelMap[r.channel]||DTX_MAP[r.channel];if(!part)continue;const n=Math.floor(r.data.length/2);for(let i=0;i<n;i++){if(r.data.slice(i*2,i*2+2)!=="00")notes.push({time:measure*secPerMeasure+(i/n)*secPerMeasure,part,velocity:.8})}}
  notes.sort((a,b)=>a.time-b.time);return {name,bpm,duration:(notes.at(-1)?.time||0)+secPerMeasure,notes};
}
