import base64, json, os, subprocess, shutil, hashlib, sys, math
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path('audio_ai_job')
for d in ['input','work','models','demucs','mdx','roformer','df','analysis','final','logs']:
    (ROOT/d).mkdir(parents=True, exist_ok=True)

SEP = os.environ.get('SEP_BIN', 'audio-separator')
DF = os.environ.get('DF_BIN', 'deepFilter')

def run(cmd, check=True):
    cmd = [str(x) for x in cmd]
    print('+', ' '.join(cmd), flush=True)
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout, flush=True)
    with (ROOT/'logs'/'commands.log').open('a', encoding='utf-8') as f:
        f.write('+ ' + ' '.join(cmd) + '\n' + p.stdout + '\n')
    if check and p.returncode:
        raise RuntimeError(f'command failed {p.returncode}: {cmd}')
    return p

# Reconstruct the source audio. It was losslessly extracted from the uploaded AAC once,
# then FLAC/base64-chunked only to cross the GitHub Actions network boundary.
parts = sorted(Path('temp').glob('audio_input.b64.part*'))
if not parts:
    raise RuntimeError('audio input chunks missing')
b64 = ''.join(p.read_text(encoding='utf-8').strip() for p in parts)
raw = base64.b64decode(b64)
ext = '.flac' if raw[:4] == b'fLaC' else ('.wav' if raw[:4] == b'RIFF' else '.bin')
src = ROOT/'input'/('source' + ext)
src.write_bytes(raw)
run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',src])
master = ROOT/'work'/'source_master.wav'
run(['ffmpeg','-y','-i',src,'-vn','-c:a','pcm_f32le',master])

a, sr = sf.read(master, dtype='float32', always_2d=True)
mono = a.mean(axis=1).astype(np.float32)
orig_n = len(mono)
duration = orig_n / sr
# Stereo context is safer for music-source separators. Reflection/reversal padding avoids a hard zero boundary.
stereo = np.repeat(mono[:,None], 2, axis=1)
need = max(int(sr * 8.0), orig_n)
chunks, flip = [stereo], True
while sum(len(x) for x in chunks) < need:
    chunks.append(stereo[::-1] if flip else stereo)
    flip = not flip
pad = np.concatenate(chunks, axis=0)[:need]
padded = ROOT/'work'/'padded_reflect_8s.wav'
sf.write(padded, pad, sr, subtype='FLOAT')

run([SEP, '--version'])
run([SEP, '--env_info'], check=False)
run([SEP, '-l', '--list_filter=vocals', '--list_limit=12'], check=False)

def sep(model, outdir, name):
    try:
        before = set(outdir.glob('*.wav'))
        run([SEP, padded, '-m', model, '--output_dir', outdir, '--output_format', 'WAV',
             '--single_stem', 'Vocals', '--model_file_dir', ROOT/'models'])
        after = list(outdir.glob('*.wav'))
        new = [p for p in after if p not in before]
        wavs = new or after
        if not wavs:
            raise RuntimeError('separator generated no WAV')
        p = max(wavs, key=lambda q: q.stat().st_mtime)
        dst = outdir/f'{name}_vocals.wav'
        if p != dst:
            shutil.copy2(p, dst)
        return dst
    except Exception as e:
        (ROOT/'logs'/f'{name}_ERROR.txt').write_text(repr(e), encoding='utf-8')
        print(name, 'FAILED:', repr(e), flush=True)
        return None

# Three genuinely different model families.
outs = {
    'demucs': sep('htdemucs_ft.yaml', ROOT/'demucs', 'demucs_htdemucs_ft'),
    'mdx': sep('UVR-MDX-NET-Inst_HQ_3.onnx', ROOT/'mdx', 'mdx_inst_hq3'),
    'roformer': sep('model_bs_roformer_ep_317_sdr_12.9755.ckpt', ROOT/'roformer', 'bs_roformer'),
}

cropped = {}
for k,p in outs.items():
    if not p:
        continue
    x, ss = sf.read(p, dtype='float32', always_2d=True)
    if ss != sr:
        tmp = ROOT/'work'/f'{k}_resampled.wav'
        run(['ffmpeg','-y','-i',p,'-ar',str(sr),tmp])
        x, ss = sf.read(tmp, dtype='float32', always_2d=True)
    x = x[:orig_n].mean(axis=1).astype(np.float32)
    if len(x) < orig_n:
        x = np.pad(x, (0, orig_n-len(x)))
    q = ROOT/'work'/f'{k}_cropped.wav'
    sf.write(q, x, sr, subtype='FLOAT')
    cropped[k] = q

if len(cropped) < 2:
    raise RuntimeError(f'Fewer than two AI separator families succeeded: {list(cropped)}')

# Speech enhancement is isolated in its own NumPy<2 environment.
dfouts = {}
for k,p in cropped.items():
    inp48 = ROOT/'df'/f'{k}_48k.wav'
    run(['ffmpeg','-y','-i',p,'-ar','48000',inp48])
    od = ROOT/'df'/f'{k}_out'
    od.mkdir(exist_ok=True)
    r = run([DF, inp48, '--output-dir', od], check=False)
    ws = list(od.glob('*.wav'))
    if r.returncode == 0 and ws:
        w = max(ws, key=lambda q: q.stat().st_mtime)
        back = ROOT/'work'/f'{k}_df_44k.wav'
        run(['ffmpeg','-y','-i',w,'-ar',str(sr),'-c:a','pcm_f32le',back])
        dfouts[k] = back
    else:
        (ROOT/'logs'/f'{k}_deepfilter_ERROR.txt').write_text(r.stdout, encoding='utf-8')

start = 0.325
end = min(duration, 1.075)
si, ei = int(start*sr), int(end*sr)
bgi = min(int(0.300*sr), orig_n)

def loadmono(p):
    x, s = sf.read(p, dtype='float32', always_2d=True)
    if s != sr:
        raise RuntimeError(f'unexpected sample rate {s} in {p}')
    y = x.mean(axis=1)
    if len(y) < orig_n:
        y = np.pad(y, (0,orig_n-len(y)))
    return y[:orig_n].astype(np.float32)

def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)) + 1e-15))

def db(x):
    return 20.0*math.log10(max(float(x),1e-12))

def corr(x,y):
    x=x-np.mean(x); y=y-np.mean(y)
    d=np.linalg.norm(x)*np.linalg.norm(y)
    return float(np.dot(x,y)/d) if d>1e-12 else 0.0

def metrics(x, ref):
    t=x[si:ei]; rt=ref[si:ei]
    br=rms(x[:bgi]); rr=rms(ref[:bgi])
    tr=rms(t); rtr=rms(rt)
    return {
        'speech_corr_to_original': corr(t,rt),
        'speech_rms_dbfs': db(tr),
        'speech_level_delta_db': db(tr)-db(rtr),
        'background_rms_dbfs': db(br),
        'background_reduction_db': db(rr)-db(br),
        'peak_dbfs': db(np.max(np.abs(x))),
        'dc_offset': float(np.mean(x)),
        'clipped_samples': int(np.sum(np.abs(x)>=0.999999)),
    }

ref = mono
cand_audio = {k:loadmono(p) for k,p in cropped.items()}
all_metrics = {k:metrics(x,ref) for k,x in cand_audio.items()}
# Preservation first: reject obviously mangled speech, then use correlation plus a capped noise-reduction benefit.
def quality(m):
    preservation = m['speech_corr_to_original']
    level_pen = max(0.0, abs(m['speech_level_delta_db'])-9.0) * 0.01
    noise_bonus = max(-3.0, min(15.0, m['background_reduction_db'])) * 0.008
    return preservation + noise_bonus - level_pen
for k,m in all_metrics.items():
    m['preservation_first_score'] = quality(m)

eligible = [k for k,m in all_metrics.items() if m['speech_corr_to_original'] >= 0.35]
if not eligible:
    eligible = list(all_metrics)
best = max(eligible, key=lambda k: all_metrics[k]['preservation_first_score'])

# Phase-safe-ish ensemble candidate: time-align other outputs to the selected reference over the speech region,
# then conservative weighted blend. It is created for comparison, not blindly selected as MASTER.
def align_to(refx, x, max_ms=25):
    maxlag = int(sr*max_ms/1000)
    r = refx[si:ei]
    z = x[si:ei]
    cc = signal.correlate(z, r, mode='full', method='fft')
    lags = signal.correlation_lags(len(z),len(r),mode='full')
    mask = np.abs(lags)<=maxlag
    lag = int(lags[mask][np.argmax(cc[mask])])
    if lag>0:
        y=np.pad(x,(0,lag))[lag:lag+len(x)]
    elif lag<0:
        y=np.pad(x,(-lag,0))[:len(x)]
    else:
        y=x.copy()
    return y.astype(np.float32), lag

refbest = cand_audio[best]
aligned = [refbest]
align_lags = {best:0}
for k,x in cand_audio.items():
    if k==best: continue
    y,lag=align_to(refbest,x)
    # RMS match speech segment before mixing, bounded to avoid amplifying artifacts.
    g=np.clip(rms(refbest[si:ei])/max(rms(y[si:ei]),1e-9),0.5,2.0)
    aligned.append(y*g)
    align_lags[k]=lag
if len(aligned)>1:
    ensemble = 0.70*aligned[0] + 0.30*np.mean(np.stack(aligned[1:]),axis=0)
else:
    ensemble = aligned[0]
ensemble = ensemble.astype(np.float32)
ens_path=ROOT/'work'/'ensemble_aligned.wav'
sf.write(ens_path,ensemble,sr,subtype='FLOAT')
all_metrics['ensemble']=metrics(ensemble,ref)

# DeepFilterNet is applied conservatively: preserve the selected separator as the majority component.
master_src = refbest.copy()
selected_df = None
if best in dfouts:
    dfx = loadmono(dfouts[best])
    dm = metrics(dfx, refbest)
    # Only mix enhancement if it still strongly follows the separator speech.
    if dm['speech_corr_to_original'] >= 0.60:
        master_src = (0.85*refbest + 0.15*dfx).astype(np.float32)
        selected_df = best

# Gentle final mastering. Avoid hard denoising and preserve articulation.
def finish(x, aggressive=False):
    y=x[si:ei].astype(np.float64)
    y-=np.mean(y)
    hp=80.0 if aggressive else 55.0
    sos=signal.butter(2,hp,btype='highpass',fs=sr,output='sos')
    y=signal.sosfiltfilt(sos,y)
    n=len(y)
    fi=min(n,int(0.008*sr)); fo=min(n,int(0.025*sr))
    if fi>1: y[:fi]*=np.linspace(0,1,fi)
    if fo>1: y[-fo:]*=np.linspace(1,0,fo)
    peak=np.max(np.abs(y))+1e-12
    target=0.82 if not aggressive else 0.86
    y*=min(target/peak, 8.0)
    y=np.clip(y,-0.95,0.95)
    return y.astype(np.float32)

master_audio=finish(master_src,False)
master24=ROOT/'final'/'utsunomiya_HQ_MASTER_24bit.wav'
sf.write(master24,master_audio,sr,subtype='PCM_24')
agg_source=loadmono(dfouts[best]) if best in dfouts else refbest
agg_audio=finish(agg_source,True)
agg24=ROOT/'final'/'utsunomiya_HQ_AGGRESSIVE_24bit.wav'
sf.write(agg24,agg_audio,sr,subtype='PCM_24')
run(['ffmpeg','-y','-i',master24,'-c:a','flac',ROOT/'final'/'utsunomiya_HQ_MASTER.flac'])
run(['ffmpeg','-y','-i',master24,'-b:a','320k',ROOT/'final'/'utsunomiya_HQ_MASTER_320k.mp3'])

# Full-length source/candidates for inspection.
shutil.copy2(master,ROOT/'final'/'source_full_before.wav')
for k,p in cropped.items(): shutil.copy2(p,ROOT/'final'/f'candidate_{k}_vocals_full.wav')
for k,p in dfouts.items(): shutil.copy2(p,ROOT/'final'/f'candidate_{k}_deepfilternet_full.wav')
shutil.copy2(ens_path,ROOT/'final'/'candidate_ensemble_full.wav')
full_after=ROOT/'final'/'source_full_after.wav'
sf.write(full_after,master_src,sr,subtype='PCM_24')

# Target-only comparison: Original | Demucs | MDX | RoFormer | DF(selected if present) | Ensemble | MASTER.
compare=[]
def target_file(name,x):
    p=ROOT/'work'/name
    sf.write(p,finish(x,False),sr,subtype='PCM_24')
    return p
compare.append(('original',target_file('ab_original.wav',ref)))
for k in ['demucs','mdx','roformer']:
    if k in cand_audio: compare.append((k,target_file(f'ab_{k}.wav',cand_audio[k])))
if best in dfouts: compare.append((f'{best}+DeepFilterNet',target_file('ab_df.wav',loadmono(dfouts[best]))))
compare.append(('ensemble',target_file('ab_ensemble.wav',ensemble)))
compare.append(('MASTER',master24))
sil=ROOT/'work'/'silence.wav'
run(['ffmpeg','-y','-f','lavfi','-i',f'anullsrc=r={sr}:cl=mono','-t','0.4','-c:a','pcm_s24le',sil])
concat=ROOT/'work'/'concat.txt'
lines=[]
for i,(_,p) in enumerate(compare):
    lines.append(f"file '{p.resolve()}'")
    if i<len(compare)-1: lines.append(f"file '{sil.resolve()}'")
concat.write_text('\n'.join(lines),encoding='utf-8')
run(['ffmpeg','-y','-f','concat','-safe','0','-i',concat,'-c:a','pcm_s24le',ROOT/'final'/'utsunomiya_AI_AB_compare.wav'])

# Model and file hashes are evidence that real weights were downloaded, not merely packages installed.
model_files=[]
for p in sorted((ROOT/'models').rglob('*')):
    if p.is_file():
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        model_files.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h})

master_metrics={
    'peak_dbfs':db(np.max(np.abs(master_audio))),
    'rms_dbfs':db(rms(master_audio)),
    'dc_offset':float(np.mean(master_audio)),
    'clipped_samples':int(np.sum(np.abs(master_audio)>=0.999999)),
}
(ROOT/'analysis'/'candidate_metrics.json').write_text(json.dumps(all_metrics,ensure_ascii=False,indent=2),encoding='utf-8')
report=[]
report.append('# PROCESS_REPORT_AI.md\n\n')
report.append(f'- Source: lossless FLAC transfer of uploaded AAC audio\n- Sample rate: {sr} Hz\n- Duration: {duration:.6f} s\n- Target trim: {start:.3f}–{end:.3f} s\n- Background profile region: 0.000–{min(0.300,duration):.3f} s\n- Context padding: reflection/reversal to 8.0 s, removed after inference\n\n')
report.append('## Actual AI inference\n')
for k in ['demucs','mdx','roformer']:
    report.append(f'- {k}: {"SUCCESS" if k in cropped else "FAILED"}\n')
report.append(f'- DeepFilterNet successful outputs: {", ".join(dfouts.keys()) or "none"}\n')
report.append(f'- Preservation-first selected separator: **{best}**\n')
report.append(f'- DeepFilterNet mixed into MASTER: **{selected_df or "no"}** (15% only when preservation check passed)\n')
report.append(f'- Ensemble alignment lags (samples): `{json.dumps(align_lags)}`\n\n')
report.append('## Candidate metrics\n```json\n'+json.dumps(all_metrics,ensure_ascii=False,indent=2)+'\n```\n\n')
report.append('## MASTER metrics\n```json\n'+json.dumps(master_metrics,ensure_ascii=False,indent=2)+'\n```\n\n')
report.append('## Downloaded model files\n')
for m in model_files:
    report.append(f'- `{m["path"]}` — {m["bytes"]} bytes — SHA256 `{m["sha256"]}`\n')
report.append('\n## AB comparison order\n'+ ' → '.join(n for n,_ in compare) + '\n\n')
report.append('## Final files\n')
for p in sorted((ROOT/'final').glob('*')):
    report.append(f'- `{p.name}` ({p.stat().st_size} bytes)\n')
(ROOT/'final'/'PROCESS_REPORT_AI.md').write_text(''.join(report),encoding='utf-8')
print('SUCCESSFUL SEPARATORS:',list(cropped))
print('DEEPFILTERNET:',list(dfouts))
print('MASTER BASE:',best)
print('MASTER METRICS:',master_metrics)
print((ROOT/'final'/'PROCESS_REPORT_AI.md').read_text(encoding='utf-8'))
