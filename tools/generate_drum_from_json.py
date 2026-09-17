from pathlib import Path
import base64
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'tools/drum_asset_source'
TARGET = ROOT / 'character-assets/layers/drum/drum_base.png'
MANIFEST = ROOT / 'character-assets/config/assets_manifest.json'
INVENTORY = ROOT / 'character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json'
EXPECTED_SHA256 = 'afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d'
EXPECTED_BYTES = 2309301
EXPECTED_SIZE = (1448, 1086)

# Preferred transport: plain Base64 text chunks. This keeps the ChatGPT->GitHub
# handoff entirely text-based while restoring the exact original PNG bytes.
b64_paths = sorted(SOURCE_DIR.glob('part_*.b64'))
if b64_paths:
    encoded = ''.join(p.read_text(encoding='utf-8').strip() for p in b64_paths)
else:
    # Backward-compatible JSON transport.
    parts = []
    for path in sorted(SOURCE_DIR.glob('part_*.json')):
        if path.name == 'READY.json':
            continue
        obj = json.loads(path.read_text(encoding='utf-8'))
        parts.append(obj['data'])
    if not parts:
        raise SystemExit('no drum source parts found')
    encoded = ''.join(parts)

raw = base64.b64decode(encoded, validate=True)
sha = hashlib.sha256(raw).hexdigest()
if len(raw) != EXPECTED_BYTES:
    raise SystemExit(f'byte-size mismatch: {len(raw)} != {EXPECTED_BYTES}')
if sha != EXPECTED_SHA256:
    raise SystemExit(f'sha256 mismatch: {sha} != {EXPECTED_SHA256}')

TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_bytes(raw)

with Image.open(TARGET) as im:
    if im.format != 'PNG':
        raise SystemExit(f'format mismatch: {im.format}')
    if im.size != EXPECTED_SIZE:
        raise SystemExit(f'image-size mismatch: {im.size} != {EXPECTED_SIZE}')
    if im.mode != 'RGBA':
        raise SystemExit(f'mode mismatch: {im.mode} != RGBA')
    a_min, a_max = im.getchannel('A').getextrema()
    if a_min != 0 or a_max != 255:
        raise SystemExit(f'alpha mismatch: {a_min}..{a_max}')

manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
manifest['lockedDrumSha256'] = sha
for item in manifest.get('assets', []):
    if item.get('path') == 'character-assets/layers/drum/drum_base.png':
        item['sha256'] = sha
        item['width'] = EXPECTED_SIZE[0]
        item['height'] = EXPECTED_SIZE[1]
        item['ready'] = True
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

inventory = json.loads(INVENTORY.read_text(encoding='utf-8'))
inventory.setdefault('qa', {})['fixedDrumSha256'] = sha
INVENTORY.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print('drum restored byte-for-byte from text chunks')
print('bytes', len(raw))
print('sha256', sha)
