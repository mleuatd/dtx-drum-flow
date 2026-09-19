import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TOOL=ROOT/'tools/reference_model/build_runtime_prototype_plan.py'
def test_plan(tmp_path):
    inv={'requiredFrames':{'neutral':{'path':'n.png','sha256':'n'},'h':{'path':'h.png','sha256':'h'},'r':{'path':'r.png','sha256':'r'}},'runtimePhaseFrameMap':{'SN:L':{'hit':'h','rebound':'r'}}}
    c={'parts':{'SN':{'approximate':{'x':420,'y':535}}}}
    t={'rules':{'normalSingle':'neutral -> hit -> rebound -> neutral'},'timings':{'hitEndSeconds':.18,'reboundEndSeconds':.28}}
    app={'x':1}; rt={'targetHeadCount':4.0}
    paths=[]
    for name,obj in [('i',inv),('c',c),('t',t),('a',app),('r',rt)]:
        p=tmp_path/(name+'.json');p.write_text(json.dumps(obj));paths.append(p)
    out=tmp_path/'out.json'
    cmd=[sys.executable,str(TOOL),'--inventory',str(paths[0]),'--contacts',str(paths[1]),'--transitions',str(paths[2]),'--appearance',str(paths[3]),'--retarget-profile',str(paths[4]),'--action-key','SN:L','--output',str(out)]
    assert subprocess.run(cmd).returncode==0
    d=json.loads(out.read_text()); assert d['sourceFrames']['hit']['id']=='h'; assert d['targetHeadCount']==4.0
