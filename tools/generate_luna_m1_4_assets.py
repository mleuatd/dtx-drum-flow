from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]

def sha256(rel):
    return hashlib.sha256((R/rel).read_bytes()).hexdigest()

def sync_paths(obj):
    if isinstance(obj,dict):
        p=obj.get('path')
        if isinstance(p,str) and p.endswith('.png') and (R/p).exists():
            obj['sha256']=sha256(p)
            if 'ready' in obj: obj['ready']=True
        for v in obj.values(): sync_paths(v)
    elif isinstance(obj,list):
        for v in obj: sync_paths(v)

manifest_path=R/'character-assets/config/assets_manifest.json'
manifest=json.loads(manifest_path.read_text())
sync_paths(manifest)
drum='character-assets/layers/drum/drum_base.png'
neutral='character-assets/layers/character/base/neutral.png'
manifest['lockedDrumSha256']=sha256(drum)
manifest['lockedNeutralSha256']=sha256(neutral)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

inv_path=R/'character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json'
inv=json.loads(inv_path.read_text())
sync_paths(inv)
inv_path.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n')

# Bump the Luna character cache token everywhere it is referenced.
for p in [R/'site/app.js',R/'site/character-prototype.js',R/'site/index.html',R/'site/styles.css']:
    if not p.exists(): continue
    s=p.read_text()
    s=s.replace('luna-m1-4-keyfix-r8','luna-m1-4-final-r9')
    s=s.replace('luna-m1-4-r8','luna-m1-4-final-r9')
    p.write_text(s)

print('metadata/hash/cache finalized')
print('neutral sha256',manifest['lockedNeutralSha256'])
print('drum sha256',manifest['lockedDrumSha256'])
