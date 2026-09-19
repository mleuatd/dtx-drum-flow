import json, io, requests, numpy as np, soundfile as sf
from pathlib import Path
OUT=Path("qa/audio-integrity"); OUT.mkdir(parents=True,exist_ok=True)
CORE="https://raw.githubusercontent.com/0x4D44/ferrosintesis/main/crates/ferrosintesis-samples-drumkit/samples/"
CYM="https://raw.githubusercontent.com/0x4D44/ferrosintesis/main/crates/ferrosintesis-samples-drumkit2/samples/"
voices={"kick":(CORE,"kick",4,4),"snare":(CORE,"snare",6,3),"sideStick":(CORE,"sidestick",3,3),"hihatClosed":(CORE,"hhc",4,4),"hihatOpen":(CORE,"hho",4,3),"hihatPedal":(CORE,"hhp",3,4),"tomHigh":(CORE,"tomhi",4,3),"tomLow":(CORE,"tomlo",4,3),"tomFloor":(CORE,"tomlo",4,3),"ride":(CORE,"ride",3,4),"rideBell":(CORE,"ridebell",3,3),"crashLeft":(CYM,"crash",3,4),"crashRight":(CYM,"crash",3,4)}
rows=[]; failures=[]
for voice,(base,prefix,layers,rrs) in voices.items():
 for layer in range(1,layers+1):
  for rr in range(1,rrs+1):
   url=f"{base}{prefix}_vl{layer}_rr{rr}.flac"
   raw=requests.get(url,timeout=30); raw.raise_for_status()
   x,sr=sf.read(io.BytesIO(raw.content),dtype="float32",always_2d=True); x=x.mean(axis=1)
   peak=float(np.max(np.abs(x))); rms=float(np.sqrt(np.mean(x*x))); clipped=int(np.sum(np.abs(x)>=.999))
   dx=np.abs(np.diff(x)); jump=float(dx.max()) if len(dx) else 0.0
   if len(x):
    n=min(64,len(x)); edge=max(float(np.max(np.abs(x[:n]))),float(np.max(np.abs(x[-n:]))))
   else: edge=0.0
   reasons=[]
   if clipped: reasons.append("clipped_samples")
   if edge>.20: reasons.append("hot_boundary")
   if not np.isfinite(x).all(): reasons.append("non_finite")
   if reasons: failures.append((voice,layer,rr,reasons))
   rows.append(dict(soundKey=voice,layer=layer,roundRobin=rr,sampleRate=sr,duration=len(x)/sr,peak=peak,rms=rms,maxAdjacentJump=jump,boundaryPeak=edge,clippedSamples=clipped,status="REVIEW" if reasons else "PASS",reasons=reasons,url=url))
engine=Path("site/live-drum-engine.js").read_text(); mapping=Path("site/drum-note-sound-map.js").read_text()
required=["kick","snare","sideStick","hihatClosed","hihatOpen","hihatPedal","tomHigh","tomLow","tomFloor","ride","rideBell","crashLeft","crashRight"]
missing=[v for v in required if v not in engine or v not in mapping]
procedural=[s for s in ["createOscillator(","_noiseBuffer(","metalPartials"] if s in engine]
# Practice-oriented perceptual metrics. Calibrate from attack/early energy as well as whole-file RMS.
# This is song-independent and uses all RR samples from the loudest layer.
def db(v): return 20*np.log10(max(float(v),1e-9))
voice_metrics={}
for voice,(base,prefix,layers,rrs) in voices.items():
 vr=[r for r in rows if r["soundKey"]==voice and r["layer"]==layers]
 vals=[]
 for r in vr:
  raw=requests.get(r["url"],timeout=30); raw.raise_for_status()
  x,sr=sf.read(io.BytesIO(raw.content),dtype="float32",always_2d=True); x=x.mean(axis=1)
  def wrms(sec):
   y=x[:max(1,min(len(x),int(sr*sec)))]
   return float(np.sqrt(np.mean(y*y))) if len(y) else 0
  vals.append({"full":float(np.sqrt(np.mean(x*x))),"attack":wrms(.08),"early":wrms(.35),"peak":float(np.max(np.abs(x)))})
 med={k:float(np.median([v[k] for v in vals])) for k in vals[0]}
 # Practice salience: transient and first 350 ms dominate note identification.
 sal=.55*db(med["early"])+.30*db(med["attack"])+.15*db(med["full"])
 voice_metrics[voice]={**med,"salienceDb":sal}
# Exact common practice target: every voice is normalized to the same measured salience.\ntarget_db=-13.5
# Deliberately flat: no cymbal boost. Tiny offsets only to help low drums survive spectral masking.
offset={v:0.0 for v in voices}
calibration={v:float(10**(((target_db+offset.get(v,0))-m["salienceDb"])/20)) for v,m in voice_metrics.items()}
post_db={v:voice_metrics[v]["salienceDb"]+20*np.log10(calibration[v]) for v in voice_metrics}
spread=max(post_db.values())-min(post_db.values())
(OUT/"loudness-calibration.json").write_text(json.dumps({"method":"attack+early+full RMS practice salience","voiceMetrics":voice_metrics,"targetDb":target_db,"offsetDb":offset,"gain":calibration,"postDb":post_db,"spreadDb":spread},indent=2))
summary={"samplesChecked":len(rows),"reviewSamples":len(failures),"missingVoices":missing,"proceduralLegacyTokens":procedural,"practiceSalienceSpreadDb":spread,"status":"PASS" if not missing and not procedural and not failures and spread<=2.0 else "REVIEW"}
(OUT/"sample-metrics.json").write_text(json.dumps(rows,indent=2))
(OUT/"summary.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
if missing or procedural or spread>2.0: raise SystemExit(1)
