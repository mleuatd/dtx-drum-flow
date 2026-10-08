"""Restore disposable candidate workspace from durable canonical sources. Run from any checkout."""
from pathlib import Path
import shutil,hashlib
r=next(p for p in Path(__file__).resolve().parents if (p/'character-assets').is_dir())
o=r.parent/'work_output'
for d in ['sources','previews','qa','scripts','variants/bd','variants/ht','variants/lt','variants/ft','variants/remaining']:(o/d).mkdir(parents=True,exist_ok=True)
sources={'neutral.png':r/'character-assets/layers/character/base/neutral.png','drum_fixed.png':r/'character-assets/layers/drum/drum_base.png'}
expected={'neutral.png':'886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9','drum_fixed.png':'dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85'}
for name,p in sources.items():
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected[name],name
 shutil.copy(p,o/'sources'/name)
for p in (r/'character-assets/production/20261008/scripts').glob('*.py'):shutil.copy(p,o/'scripts'/p.name)
print('Restored',o,'from protected canonical sources. Formal60PNG already exist; regenerate candidates only if repairing a concrete defect.')
