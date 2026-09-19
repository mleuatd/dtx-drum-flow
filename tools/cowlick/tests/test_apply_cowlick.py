import json, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
TOOL=ROOT/'tools/cowlick/apply_cowlick.py'
PROFILE=ROOT/'tools/cowlick/profiles/luna_3q_back_left_v1.json'

def test_outside_roi_unchanged(tmp_path):
    src=tmp_path/'src.png'; out=tmp_path/'out.png'; qa=tmp_path/'qa.json'
    Image.new('RGBA',(1448,1086),(255,255,255,0)).save(src)
    subprocess.run([sys.executable,str(TOOL),'--input',str(src),'--profile',str(PROFILE),'--output',str(out),'--qa-report',str(qa)],check=True)
    report=json.loads(qa.read_text())
    assert report['outsideRoiChangedPixels']==0
    assert report['insideRoiChangedPixels']>0

def test_sha_guard(tmp_path):
    src=tmp_path/'src.png'; out=tmp_path/'out.png'; qa=tmp_path/'qa.json'
    Image.new('RGBA',(1448,1086),(255,255,255,0)).save(src)
    p=subprocess.run([sys.executable,str(TOOL),'--input',str(src),'--profile',str(PROFILE),'--output',str(out),'--qa-report',str(qa),'--expected-source-sha256','0'*64])
    assert p.returncode!=0
