import base64, json, os, subprocess, glob, shutil, hashlib, sys
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT=Path('audio_ai_job')
for d in ['input','work','models','demucs','mdx','roformer','df','final','logs']:
    (ROOT/d).mkdir(parents=True, exist_ok=True)

def run(cmd, check=True):
    print('+', ' '.join(map(str,cmd)), flush=True)
    p=subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout, flush=True)
    (ROOT/'logs'/'commands.log').open('a').write('+ '+' '.join(map(str,cmd))+'\n'+p.stdout+'\n')
    if check and p.returncode: raise RuntimeError(f'command failed {p.returncode}: {cmd}')
    return p

b64=Path('temp/audio_input.b64').read_text().strip()
video=ROOT/'input'/'source.mp4'
video.write_bytes(base64.b64decode(b64))
run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)])
master=ROOT/'work'/'source_master.wav'
run(['ffmpeg','-y','-i',str(video),'-vn','-c:a','pcm_f32le',str(master)])

a,sr=sf.read(master,dtype='float32',always_2d=True)
if a.shape[1]==1: a=np.repeat(a,2,axis=1)
orig_n=len(a)
need=max(int(sr*8.0),orig_n)
chunks=[a]; flip=False
while sum(len(x) for x in chunks)<need:
    chunks.append(a[::-1] if not flip else a)
    flip=not flip
pad=np.concatenate(chunks,axis=0)[:need]
padded=ROOT/'work'/'padded_reflect_8s.wav'
sf.write(padded,pad,sr,subtype='FLOAT')

run([sys.executable,'-V'])
run(['audio-separator','--version'])
run(['audio-separator','--env_info'])
run(['audio-separator','-l','--list_filter=vocals','--list_limit=8'],check=False)

def sep(model,outdir,name):
    try:
        run(['audio-separator',str(padded),'-m',model,'--output_dir',str(outdir),'--output_format','WAV','--single_stem','Vocals','--model_file_dir',str(ROOT/'models')])
        wavs=sorted(outdir.glob('*.wav'),key=lambda p:p.stat().st_mtime)
        if not wavs: raise RuntimeError('no wav output')
        dst=outdir/f'{name}_vocals.wav'
        if wavs[-1]!=dst: shutil.copy2(wavs[-1],dst)
        return dst
    except Exception as e:
        (ROOT/'logs'/f'{name}_ERROR.txt').write_text(repr(e))
        return None

outs={}
outs['demucs']=sep('htdemucs_ft.yaml',ROOT/'demucs','demucs_htdemucs_ft')
outs['mdx']=sep('UVR-MDX-NET-Inst_HQ_3.onnx',ROOT/'mdx','mdx_inst_hq3')
outs['roformer']=sep('model_bs_roformer_ep_317_sdr_12.9755.ckpt',ROOT/'roformer','bs_roformer')

cropped={}
for k,p in outs.items():
    if not p: continue
    x,ss=sf.read(p,dtype='float32',always_2d=True)
    if ss!=sr:
        tmp=ROOT/'work'/f'{k}_resampled.wav'
        run(['ffmpeg','-y','-i',str(p),'-ar',str(sr),str(tmp)])
        x,ss=sf.read(tmp,dtype='float32',always_2d=True)
    x=x[:orig_n]
    x=x.mean(axis=1)
    q=ROOT/'work'/f'{k}_cropped.wav'; sf.write(q,x,sr,subtype='FLOAT'); cropped[k]=q

dfouts={}
for k,p in cropped.items():
    inp48=ROOT/'df'/f'{k}_48k.wav'
    run(['ffmpeg','-y','-i',str(p),'-ar','48000',str(inp48)])
    od=ROOT/'df'/f'{k}_out'; od.mkdir(exist_ok=True)
    run(['deepFilter',str(inp48),'--output-dir',str(od)],check=False)
    ws=list(od.glob('*.wav'))
    if ws:
        back=ROOT/'work'/f'{k}_df_44k.wav'
        run(['ffmpeg','-y','-i',str(ws[0]),'-ar',str(sr),str(back)])
        dfouts[k]=back

start=0.325
end=min(orig_n/sr,1.075)

def trim_norm(src,dst,aggressive=False):
    filt=f'atrim=start={start}:end={end},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.008,afade=t=out:st={max(0,end-start-0.025):.4f}:d=0.025'
    if aggressive: filt += ',highpass=f=90,lowpass=f=12000,acompressor=threshold=-24dB:ratio=2:attack=8:release=80:makeup=2dB,alimiter=limit=0.92'
    else: filt += ',highpass=f=65,acompressor=threshold=-28dB:ratio=1.35:attack=12:release=120:makeup=1.5dB,alimiter=limit=0.90'
    run(['ffmpeg','-y','-i',str(src),'-af',filt,'-c:a','pcm_s24le',str(dst)])

order=['roformer','demucs','mdx']
best=next((k for k in order if k in cropped),None)
if best is None: raise RuntimeError('No AI separator succeeded')
base=cropped[best]
base_df=dfouts.get(best)
if base_df:
    blend=ROOT/'work'/'master_blend.wav'
    run(['ffmpeg','-y','-i',str(base),'-i',str(base_df),'-filter_complex','[0:a]volume=0.80[a0];[1:a]volume=0.20[a1];[a0][a1]amix=inputs=2:normalize=0','-c:a','pcm_f32le',str(blend)])
    master_src=blend
else: master_src=base

master24=ROOT/'final'/'utsunomiya_HQ_MASTER_24bit.wav'; trim_norm(master_src,master24,False)
agg24=ROOT/'final'/'utsunomiya_HQ_AGGRESSIVE_24bit.wav'; trim_norm(base_df or base,agg24,True)
run(['ffmpeg','-y','-i',str(master24),'-c:a','flac',str(ROOT/'final'/'utsunomiya_HQ_MASTER.flac')])
run(['ffmpeg','-y','-i',str(master24),'-b:a','320k',str(ROOT/'final'/'utsunomiya_HQ_MASTER_320k.mp3')])
for k,p in cropped.items(): shutil.copy2(p,ROOT/'final'/f'candidate_{k}_vocals_full.wav')
for k,p in dfouts.items(): shutil.copy2(p,ROOT/'final'/f'candidate_{k}_deepfilternet_full.wav')
shutil.copy2(master,ROOT/'final'/'source_full_before.wav')

parts=[]
orig_target=ROOT/'work'/'orig_target.wav'; trim_norm(master,orig_target,False); parts.append(orig_target)
for k in ['demucs','mdx','roformer']:
    if k in cropped:
        q=ROOT/'work'/f'{k}_target.wav'; trim_norm(cropped[k],q,False); parts.append(q)
parts.append(master24)
listf=ROOT/'work'/'concat.txt'
sil=ROOT/'work'/'silence.wav'; run(['ffmpeg','-y','-f','lavfi','-i','anullsrc=r=44100:cl=mono','-t','0.4','-c:a','pcm_s24le',str(sil)])
seq=[]
for i,p in enumerate(parts):
    seq.append(f"file '{p.resolve()}'")
    if i<len(parts)-1: seq.append(f"file '{sil.resolve()}'")
listf.write_text('\n'.join(seq))
run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(listf),'-c:a','pcm_s24le',str(ROOT/'final'/'utsunomiya_AI_AB_compare.wav')])

report=[]
report.append('# PROCESS_REPORT_AI.md\n')
report.append(f'- Source sample rate: {sr} Hz\n- Source samples: {orig_n}\n- Target trim: {start:.3f}–{end:.3f} s\n- Padding: reflection/reversal context to 8.0 s, removed after inference\n')
report.append('## Actual model execution\n')
for k in ['demucs','mdx','roformer']:
    report.append(f'- {k}: {"SUCCESS" if k in cropped else "FAILED"}\n')
report.append(f'- DeepFilterNet outputs: {", ".join(dfouts.keys()) or "none"}\n- MASTER base: {best}\n')
report.append('## Downloaded model files\n')
for p in sorted((ROOT/'models').rglob('*')):
    if p.is_file():
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        report.append(f'- `{p}` — {p.stat().st_size} bytes — SHA256 `{h}`\n')
report.append('\n## Final files\n')
for p in sorted((ROOT/'final').glob('*')):
    report.append(f'- `{p.name}` ({p.stat().st_size} bytes)\n')
(ROOT/'final'/'PROCESS_REPORT_AI.md').write_text(''.join(report))
print('BEST',best)
print((ROOT/'final'/'PROCESS_REPORT_AI.md').read_text())
