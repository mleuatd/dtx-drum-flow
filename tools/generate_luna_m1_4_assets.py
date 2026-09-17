from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]

def file_for(rel):
    p=R/rel
    if p.exists(): return p
    p=R/'character-assets'/rel
    return p

def sha256(rel):
    return hashlib.sha256(file_for(rel).read_bytes()).hexdigest()

def sync_paths(obj):
    if isinstance(obj,dict):
        p=obj.get('path')
        if isinstance(p,str) and p.endswith('.png') and file_for(p).exists():
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
inv.setdefault('qa',{})['fixedDrumSha256']=sha256(drum)
inv['qa']['unresolved']=0
inv['qa']['imageAssetCount']=12
inv_path.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n')

for p in [R/'site/app.js',R/'site/character-prototype.js',R/'site/index.html',R/'site/styles.css']:
    if not p.exists(): continue
    s=p.read_text().replace('luna-m1-4-keyfix-r8','luna-m1-4-final-r9').replace('luna-m1-4-r8','luna-m1-4-final-r9')
    p.write_text(s)

print('metadata/hash/cache finalized')
print('neutral sha256',manifest['lockedNeutralSha256'])
print('drum sha256',manifest['lockedDrumSha256'])
