import hashlib,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];T=ROOT/'tools/line_style/image_to_dessin_v3.py';P=ROOT/'tools/line_style/profiles/dessin_sharppen_clean_v3.json'
def test_sharppen_v3(tmp_path):
 s=tmp_path/'s.png';im=Image.new('RGB',(80,60),'white');d=ImageDraw.Draw(im);d.rectangle((10,10,70,50),outline='black',width=1);im.save(s)
 def run(n):
  o=tmp_path/f'{n}.png';q=tmp_path/f'{n}.json';r=subprocess.run([sys.executable,str(T),'--input',str(s),'--output',str(o),'--profile',str(P),'--qa-report',str(q)]);return r,o,json.loads(q.read_text())
 r,a,q=run('a');r2,b,q2=run('b');assert r.returncode==0 and r2.returncode==0;assert hashlib.sha256(a.read_bytes()).digest()==hashlib.sha256(b.read_bytes()).digest();assert q['maximumStrokeWidthInternalPx']==1 and q['effectiveBaseStrokeWidthFinalPx']<=.25 and q['solidFillRatio']==0
