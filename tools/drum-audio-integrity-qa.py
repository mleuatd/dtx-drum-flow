import json, os, re, io, requests, numpy as np, soundfile as sf
from pathlib import Path
OUT=Path("qa/audio-integrity"); OUT.mkdir(parents=True,exist_ok=True)
CORE="https://raw.githubusercontent.com/0x4D44/ferrosintesis/main/crates/ferrosintesis-samples-drumkit/samples/"
CYM="https://raw.githubusercontent.com/0x4D44/ferrosintesis/main/crates/ferrosintesis-samples-drumkit2/samples/"
voices={"kick":(CORE,"kick",4,4),"snare":(CORE,"snare",6,3),"sideStick":(CORE,"sidestick",3,3),"hihatClosed":(CORE,"hhc",4,4),"hihatOpen":(CORE,"hho",4,3),"hihatPedal":(CORE,"hhp",3,4),"tomHigh":(CORE,"tomhi",4,3),"tomLow":(CORE,"tomlo",4,3),"tomFloor":(CORE,"tomlo",4,3),"ride":(CORE,"ride",3,4),"rideBell":(CORE,"ridebell",3,3),"crashLeft":(CYM,"crash",3,4),"crashRight":(CYM,"crash",3,4)}
rows=[]; failures=[]
for voice,(base,prefix,layers,rrs) in voices.items():
 for layer in range(1,layers+1):
  for rr in range(1,rrs+1):
   url=f"{base}{prefix}_vl{layer}_rr{rr}.flac"; raw=requests.get(url,timeout=30); raw.raise_for_status()
   x,sr=sf.read(io.BytesIO(raw.content),dtype="float32",always_2d=True); x=x.mean(axis=1)
   peak=float(np.max(np.abs(x))); rms=float(np.sqrt(np.mean(x*x))); clipped=int(np.sum(np.abs(x)>=.999))
   dx=np.abs(np.diff(x)); jump=float(dx.max()) if len(dx) else 0
   # clicks at file boundaries are especially suspicious; normal drum transients inside the file are not.
   edge=max(float(np.max(np.abs(x[:min(64,len(x))]))),float(np.max(np.abs(x[-min(64,len(x)):]))) if len(x) else 0
   status="PASS"
   reasons=[]
   if clipped: reasons.append("clipped_samples")
   if edge>.20: reasons.append("hot_boundary")
   if not np.isfinite(x).all(): reasons.append("non_finite")
   if reasons: status="REVIEW"; failures.append((voice,layer,rr,reasons))
   rows.append(dict(soundKey=voice,layer=layer,roundRobin=rr,sampleRate=sr,duration=len(x)/sr,peak=peak,rms=rms,maxAdjacentJump=jump,boundaryPeak=edge,clippedSamples=clipped,status=status,reasons=reasons,url=url))
# Static integration checks: every public part has a voice and no obsolete procedural primitives remain in engine.
engine=Path("site/live-drum-engine.js").read_text()
mapping=Path("site/drum-note-sound-map.js").read_text()
required=["kick","snare","sideStick","hihatClosed","hihatOpen","hihatPedal","tomHigh","tomLow","tomFloor","ride","rideBell","crashLeft","crashRight"]
missing=[v for v in required if v not in engine or v not in mapping]
procedural=[s for s in ["createOscillator(","_noiseBuffer(","metalPartials"] if s in engine]
summary={"samplesChecked":len(rows),"reviewSamples":len(failures),"missingVoices":missing,"proceduralLegacyTokens":procedural,"status":"PASS" if not missing and not procedural and not failures else "REVIEW"}
(OUT/"sample-metrics.json").write_text(json.dumps(rows,indent=2))
(OUT/"summary.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
if missing or procedural: raise SystemExit(1)
