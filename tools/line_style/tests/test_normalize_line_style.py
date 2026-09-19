import hashlib,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[3]
TOOL=ROOT/'tools/line_style/normalize_line_style.py'; VERIFY=ROOT/'tools/line_style/verify_line_style_normalization.py'
PROFILE=ROOT/'tools/line_style/profiles/luna_pencil_style_v1.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def synthetic(p):
    im=Image.new('RGBA',(1448,1086),(0,0,0,0)); d=ImageDraw.Draw(im)
    for off in [0,1,-1]: d.line((250+off,250,850+off,650),fill=(30,30,30,180),width=1)
    d.line((400,700,1000,700),fill=(20,20,20,210),width=1); im.save(p)
def run(src,out,qa,expected=None):
    c=[sys.executable,str(TOOL),'--input',str(src),'--profile',str(PROFILE),'--output',str(out),'--qa-report',str(qa)]
    if expected:c += ['--expected-source-sha256',expected]
    return subprocess.run(c)
def test_deterministic_repeatability(tmp_path):
    src=tmp_path/'s.png'; synthetic(src); a=tmp_path/'a.png'; b=tmp_path/'b.png'
    assert run(src,a,tmp_path/'a.json').returncode==0; assert run(src,b,tmp_path/'b.json').returncode==0; assert sha(a)==sha(b)
def test_sha_guard(tmp_path):
    src=tmp_path/'s.png'; synthetic(src); assert run(src,tmp_path/'o.png',tmp_path/'q.json','0'*64).returncode!=0
def test_source_overwrite_refused(tmp_path):
    src=tmp_path/'s.png'; synthetic(src); assert run(src,src,tmp_path/'q.json').returncode!=0
def test_verify_geometry(tmp_path):
    src=tmp_path/'s.png'; synthetic(src); out=tmp_path/'o.png'; qa=tmp_path/'q.json'; vr=tmp_path/'v.json'
    assert run(src,out,qa).returncode==0
    r=subprocess.run([sys.executable,str(VERIFY),'--before',str(src),'--after',str(out),'--profile',str(PROFILE),'--report',str(vr)])
    assert r.returncode==0; assert json.loads(vr.read_text())['verdict']=='PASS'
def test_corrupted_profile_fails(tmp_path):
    src=tmp_path/'s.png'; synthetic(src); bad=tmp_path/'bad.json'; p=json.loads(PROFILE.read_text()); p['baseLineWidthPx']=4; bad.write_text(json.dumps(p))
    r=subprocess.run([sys.executable,str(TOOL),'--input',str(src),'--profile',str(bad),'--output',str(tmp_path/'o.png'),'--qa-report',str(tmp_path/'q.json')])
    assert r.returncode!=0
