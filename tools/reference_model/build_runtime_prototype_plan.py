#!/usr/bin/env python3
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inventory',required=True)
    ap.add_argument('--contacts',required=True)
    ap.add_argument('--transitions',required=True)
    ap.add_argument('--appearance',required=True)
    ap.add_argument('--retarget-profile',required=True)
    ap.add_argument('--action-key',default='SN:L')
    ap.add_argument('--output',required=True)
    a=ap.parse_args()
    inv=json.loads(Path(a.inventory).read_text())
    contacts=json.loads(Path(a.contacts).read_text())
    trans=json.loads(Path(a.transitions).read_text())
    app=json.loads(Path(a.appearance).read_text())
    rt=json.loads(Path(a.retarget_profile).read_text())
    pm=inv.get('runtimePhaseFrameMap',{}).get(a.action_key)
    if not pm: raise SystemExit(f'actionKey not found in runtimePhaseFrameMap: {a.action_key}')
    parts=a.action_key.split(':',1)[0].split('+')
    contact={p:contacts.get('parts',{}).get(p) for p in parts}
    neutral=inv['requiredFrames']['neutral']
    def frame(fid):
        f=inv['requiredFrames'].get(fid)
        if not f: raise SystemExit(f'missing frame id {fid}')
        return {'id':fid,**f}
    out={
      'schemaVersion':1,'type':'runtime_character_prototype_plan','status':'READY_FOR_NUMERIC_POSE_AND_RENDER',
      'actionKey':a.action_key,'targetHeadCount':rt['targetHeadCount'],
      'northStar':'runtime-ready character frames that visibly perform the chart against the fixed drum',
      'appearanceModel':a.appearance,'retargetProfile':a.retarget_profile,
      'sourceFrames':{'neutral':{'id':'neutral',**neutral},'hit':frame(pm['hit']),'rebound':frame(pm['rebound'])},
      'instrumentContacts':contact,
      'transition':{'normalSingle':trans['rules']['normalSingle'],'hitEndSeconds':trans['timings']['hitEndSeconds'],'reboundEndSeconds':trans['timings']['reboundEndSeconds']},
      'pipeline':['extract numeric pose from existing formal frame','apply video-derived appearance constraints','retarget/validate at 4.0 heads','constrained render candidate','cowlick deterministic tool','line-style deterministic tool','fixed-drum composite QA','runtime PC/Xperia QA'],
      'formalOverwriteAllowed':False
    }
    Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
