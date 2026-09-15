from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import mido

GM_FAMILY = {
    35:"kick",36:"kick",37:"snare",38:"snare",39:"snare",40:"snare",
    41:"toms",43:"toms",45:"toms",47:"toms",48:"toms",50:"toms",
    42:"hihat",44:"hihat",46:"hihat",
    49:"cymbals",51:"cymbals",52:"cymbals",53:"cymbals",55:"cymbals",57:"cymbals",59:"cymbals",
}

def midi_notes(path: Path) -> list[tuple[float,str]]:
    mid=mido.MidiFile(path)
    tempo=500000
    t=0.0
    out=[]
    for msg in mido.merge_tracks(mid.tracks):
        t += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
        if msg.type=="set_tempo":
            tempo=msg.tempo
        elif msg.type=="note_on" and msg.velocity>0:
            out.append((t, GM_FAMILY.get(msg.note,"unknown")))
    return out

def json_notes(path: Path) -> list[tuple[float,str]]:
    data=json.loads(path.read_text(encoding="utf-8"))
    return [(float(n["time"]), str(n.get("kind","unknown"))) for n in data["notes"]]

def load(path: Path):
    return json_notes(path) if path.suffix.lower()==".json" else midi_notes(path)

def score(pred, ref, tol: float, family_sensitive: bool=True) -> dict[str,Any]:
    used=set()
    errors=[]
    tp=0
    per={}
    for pt,pk in pred:
        best=None
        best_d=10**9
        for i,(rt,rk) in enumerate(ref):
            if i in used: continue
            if family_sensitive and pk!="unknown" and rk!="unknown" and pk!=rk: continue
            d=abs(pt-rt)
            if d<=tol and d<best_d:
                best=i;best_d=d
        if best is not None:
            used.add(best);tp+=1;errors.append(best_d)
            fam=pk if pk!="unknown" else ref[best][1]
            per.setdefault(fam,[0,0,0]);per[fam][0]+=1
    fp=len(pred)-tp
    fn=len(ref)-tp
    precision=tp/max(1,tp+fp)
    recall=tp/max(1,tp+fn)
    f1=2*precision*recall/max(1e-12,precision+recall)
    for fam in set([x[1] for x in pred]+[x[1] for x in ref]):
        if fam=="unknown": continue
        pcount=sum(1 for _,k in pred if k==fam)
        rcount=sum(1 for _,k in ref if k==fam)
        hit=per.get(fam,[0])[0]
        pp=hit/max(1,pcount); rr=hit/max(1,rcount); ff=2*pp*rr/max(1e-12,pp+rr)
        per[fam]={"tp":hit,"pred":pcount,"ref":rcount,"precision":pp,"recall":rr,"f1":ff}
    return {
        "tolerance_ms":tol*1000,
        "tp":tp,"fp":fp,"fn":fn,
        "precision":precision,"recall":recall,"f1":f1,
        "mean_abs_error_ms":(sum(errors)/len(errors)*1000 if errors else None),
        "p95_abs_error_ms":(sorted(errors)[int((len(errors)-1)*.95)]*1000 if errors else None),
        "per_family":per,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("prediction",type=Path,help="notes.json または MIDI")
    ap.add_argument("reference",type=Path,help="正解 MIDI")
    ap.add_argument("-o","--output",type=Path)
    args=ap.parse_args()
    pred=load(args.prediction); ref=load(args.reference)
    result={"prediction_count":len(pred),"reference_count":len(ref),"scores":[score(pred,ref,.025),score(pred,ref,.050),score(pred,ref,.100)]}
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.output: args.output.write_text(text,encoding="utf-8")

if __name__=="__main__":
    main()
