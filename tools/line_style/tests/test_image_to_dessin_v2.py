import hashlib,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]; TOOL=ROOT/'tools/line_style/image_to_dessin_v2.py'; PROFILE=ROOT/'tools/line_style/profiles/dessin_rough_v2.json'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def src(p):
 im=Image.new('RGB',(160,120),'white');d=ImageDraw.Draw(im);d.rectangle((30,20,125,100),outline='black',width=1)
 for x in range(40,120,8):d.line((x,25,x,95),fill='black',width=1)
 im.save(p)
def run(s,o,q):return subprocess.run([sys.executable,str(TOOL),'--input',str(s),'--output',str(o),'--profile',str(PROFILE),'--qa-report',str(q)])
def test_v2_deterministic_and_thin(tmp_path):
 s=tmp_path/'s.png';src(s);a=tmp_path/'a.png';b=tmp_path/'b.png';qa=tmp_path/'q.json'
 assert run(s,a,qa).returncode==0 and run(s,b,tmp_path/'q2.json').returncode==0 and h(a)==h(b)
 q=json.loads(qa.read_text());assert q['baseStrokeWidth']==1 and q['noSolidFill'] is True and q['renderedStrokePasses']>=10
