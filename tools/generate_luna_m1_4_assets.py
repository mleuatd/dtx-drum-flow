from pathlib import Path
import base64,json,zlib,io
from PIL import Image
R=Path(__file__).resolve().parents[1]
D={}
for n in range(1,4):
    part=R/f"tools/luna_m1_4_assets_part{n}.json"
    D.update(json.loads(part.read_text()))
OUT={
"drum":"character-assets/layers/drum/drum_base.png",
"neutral":"character-assets/layers/character/base/neutral.png",
"sn_l_hit":"character-assets/layers/character/sn/hit_l.png",
"sn_l_rebound":"character-assets/layers/character/sn/rebound_l.png",
"sn_r_hit":"character-assets/layers/character/sn/hit_r.png",
"sn_r_rebound":"character-assets/layers/character/sn/rebound_r.png",
"hh_r_hit":"character-assets/layers/character/hh/hit_r.png",
"hh_r_rebound":"character-assets/layers/character/hh/rebound_r.png",
"bd_rf_hit":"character-assets/layers/character/bd/hit_rf.png",
"bd_rf_rebound":"character-assets/layers/character/bd/rebound_rf.png",
"bd_rc_hit":"character-assets/layers/character/combo/bd_rc_hit.png",
"bd_rc_rebound":"character-assets/layers/character/combo/bd_rc_rebound.png"}
palette=[(0,0,0,0),(0,0,0,255),(255,255,255,255)]
for key,path in OUT.items():
    packed=base64.b64decode(D[key])
    raw=zlib.decompress(packed)
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        rgba=Image.open(io.BytesIO(raw)).convert("RGBA")
    else:
        expected=181*136
        if len(raw)!=expected:
            raise ValueError(f"{key}: decoded length {len(raw)} != {expected}")
        src=Image.frombytes("L",(181,136),raw)
        rgba=Image.new("RGBA",src.size)
        rgba.putdata([palette[v] if v < len(palette) else palette[1] for v in src.getdata()])
    rgba=rgba.resize((1448,1088),Image.Resampling.NEAREST).crop((0,0,1448,1086))
    p=R/path;p.parent.mkdir(parents=True,exist_ok=True);rgba.save(p,optimize=True)
    print(key, p, p.stat().st_size)
print("generated",len(OUT))

# resilient materializer for Luna m1-4 binary assets
