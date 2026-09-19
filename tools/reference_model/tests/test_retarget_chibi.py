import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TOOL=ROOT/'tools/reference_model/retarget_chibi.py'
PROFILE=ROOT/'tools/reference_model/profiles/luna_video_multiview_v1.json'

def test_retarget_four_heads(tmp_path):
    pose={'joints':{'head_top':[100,0],'chin':[100,100],'shoulder_l':[70,130],'shoulder_r':[130,130],
      'elbow_l':[55,220],'elbow_r':[145,220],'wrist_l':[50,300],'wrist_r':[150,300],
      'hip_l':[80,400],'hip_r':[120,400],'knee_l':[80,600],'knee_r':[120,600],
      'ankle_l':[80,800],'ankle_r':[120,800]}}
    p=tmp_path/'pose.json'; o=tmp_path/'out.json'; p.write_text(json.dumps(pose))
    r=subprocess.run([sys.executable,str(TOOL),'--model',str(PROFILE),'--pose',str(p),'--output',str(o),'--target-head-count','4.0'])
    assert r.returncode==0
    d=json.loads(o.read_text()); assert d['targetHeadCount']==4.0
    assert d['joints']['head_top'][1]==0 and d['joints']['chin'][1]==100
    assert max(d['joints']['ankle_l'][1],d['joints']['ankle_r'][1]) <= 401
