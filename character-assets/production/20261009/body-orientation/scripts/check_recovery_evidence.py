from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[5];O=R/'character-assets/production/20261009/body-orientation'
report=json.loads((O/'qa/resume_attempt_20261009.json').read_text());checks=[]
for e in report['trials']:
 p=R/e['file'];a=np.array(Image.open(p).convert('RGBA'));b=np.array(Image.open(R/f"character-assets/layers/character/rc/{e['phase']}_r_refresh.png").convert('RGBA'))
 assert np.array_equal(a[590:],b[590:]),p
 e['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();checks.append({'path':e['file'],'lower_y590_equal':True,'visualStatus':'REJECTED'})
for p,sha in report['protectedSourceHashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==sha,p
report['mechanicalProtection']={'formalSourceFilesUnchanged':True,'candidateLowerBodiesIdentical':checks};report['acceptedPairs']=0
(O/'qa/resume_attempt_20261009.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('Protected formal sources unchanged; all candidates remain REJECTED.')
