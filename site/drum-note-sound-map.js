// Resolves every chart note to a playable live-drum voice.
// Resolution order: explicit soundKey/articulation -> GM note -> DTX part -> default voice.

export const DEFAULT_DRUM_VOICE = Object.freeze({
  voice: "snare",
  part: "SN",
  articulation: "center",
  reason: "default-unmapped-note"
});

const PART_VOICES = Object.freeze({
  BD:{voice:"kick",part:"BD",articulation:"beater"},
  LB:{voice:"kick",part:"BD",articulation:"beater"},
  SN:{voice:"snare",part:"SN",articulation:"center"},
  HH:{voice:"hihatClosed",part:"HH",articulation:"closed"},
  LP:{voice:"hihatPedal",part:"LP",articulation:"pedal"},
  HT:{voice:"tomHigh",part:"HT",articulation:"center"},
  LT:{voice:"tomLow",part:"LT",articulation:"center"},
  FT:{voice:"tomFloor",part:"FT",articulation:"center"},
  RD:{voice:"ride",part:"RD",articulation:"bow"},
  LC:{voice:"crashLeft",part:"LC",articulation:"edge"},
  RC:{voice:"crashRight",part:"RC",articulation:"edge"}
});

const GM_VOICES = Object.freeze({
  35:{voice:"kick",part:"BD",articulation:"acoustic"},
  36:{voice:"kick",part:"BD",articulation:"beater"},
  37:{voice:"sideStick",part:"SN",articulation:"cross-stick"},
  38:{voice:"snare",part:"SN",articulation:"center"},
  40:{voice:"snare",part:"SN",articulation:"rim"},
  41:{voice:"tomFloor",part:"FT",articulation:"center"},
  43:{voice:"tomFloor",part:"FT",articulation:"center"},
  45:{voice:"tomLow",part:"LT",articulation:"center"},
  47:{voice:"tomLow",part:"LT",articulation:"center"},
  48:{voice:"tomHigh",part:"HT",articulation:"center"},
  50:{voice:"tomHigh",part:"HT",articulation:"center"},
  42:{voice:"hihatClosed",part:"HH",articulation:"closed"},
  44:{voice:"hihatClosed",part:"HH",articulation:"pedal"},
  46:{voice:"hihatOpen",part:"HH",articulation:"open"},
  49:{voice:"crashLeft",part:"LC",articulation:"edge"},
  51:{voice:"ride",part:"RD",articulation:"bow"},
  52:{voice:"crashRight",part:"RC",articulation:"edge"},
  53:{voice:"rideBell",part:"RD",articulation:"bell"},
  55:{voice:"crashLeft",part:"LC",articulation:"splash"},
  57:{voice:"crashRight",part:"RC",articulation:"edge"},
  59:{voice:"ride",part:"RD",articulation:"edge"}
});

const EXPLICIT_VOICES = Object.freeze({
  kick:{voice:"kick",part:"BD"},
  snare:{voice:"snare",part:"SN"},
  sideStick:{voice:"sideStick",part:"SN"},
  hihatClosed:{voice:"hihatClosed",part:"HH"},
  hihatOpen:{voice:"hihatOpen",part:"HH"},
  hihatPedal:{voice:"hihatPedal",part:"LP"},
  tomHigh:{voice:"tomHigh",part:"HT"},
  tomLow:{voice:"tomLow",part:"LT"},
  tomFloor:{voice:"tomFloor",part:"FT"},
  ride:{voice:"ride",part:"RD"},
  rideBell:{voice:"rideBell",part:"RD"},
  crashLeft:{voice:"crashLeft",part:"LC"},
  crashRight:{voice:"crashRight",part:"RC"}
});

export function resolveDrumVoice(note={},part=note.part){
  const explicit=note.soundKey||note.voice||note.drumVoice;
  if(explicit&&EXPLICIT_VOICES[explicit])return {...EXPLICIT_VOICES[explicit],articulation:note.articulation||EXPLICIT_VOICES[explicit].articulation||"default",reason:"explicit"};
  const gm=Number(note.gmNote);
  if(Number.isFinite(gm)&&GM_VOICES[gm])return {...GM_VOICES[gm],reason:"gmNote"};
  if(part&&PART_VOICES[part])return {...PART_VOICES[part],reason:"part"};
  return {...DEFAULT_DRUM_VOICE,originalPart:part||null,originalGmNote:Number.isFinite(gm)?gm:null};
}

export function applyDrumVoice(note={},part=note.part){
  const resolved=resolveDrumVoice(note,part);
  const gmByVoice={sideStick:37,hihatOpen:46,hihatClosed:42,hihatPedal:44,ride:51,rideBell:53,crashLeft:49,crashRight:57};
  return {part:resolved.part,note:{...note,soundKey:resolved.voice,articulation:resolved.articulation,gmNote:Number.isFinite(Number(note.gmNote))?Number(note.gmNote):(gmByVoice[resolved.voice]??note.gmNote),soundResolution:resolved.reason},resolved};
}
