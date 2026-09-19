from __future__ import annotations
import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CHAR = ROOT / "character-assets/layers/character"
DRUM = ROOT / "character-assets/layers/drum/drum_base.png"
OUT = ROOT / "character-assets/review-candidates/m68"
QA = ROOT / "character-assets/generated-qa/m68"

PARENTS = {
    "hit": (
        CHAR / "combo/rc_sn_hit_refresh.png",
        "f85cb4428d653b496938e50bbc486a2ddcab2a6d388884725946ba6d64e86a82",
    ),
    "rebound": (
        CHAR / "combo/rc_sn_rebound_refresh.png",
        "1d64993260679bdf998bff85fec5d6993a004555fb98c46536177780ce38b5da",
    ),
}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add_proven_bd_cue(im: Image.Image, phase: str) -> Image.Image:
    # Exact BD cue geometry already used successfully by the repository's
    # M18-24 deterministic builder and inherited by M47/M54 derivations.
    scale = 4
    layer = Image.new("RGBA", (im.width * scale, im.height * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    if phase == "hit":
        segments = [
            ((470, 820), (452, 805)),
            ((482, 815), (474, 792)),
            ((495, 817), (494, 791)),
        ]
    else:
        segments = [((482, 820), (470, 810))]
    for a, b in segments:
        draw.line(
            [(a[0] * scale, a[1] * scale), (b[0] * scale, b[1] * scale)],
            fill=(18, 18, 18, 255),
            width=4 * scale,
        )
    cue = layer.resize(im.size, Image.Resampling.LANCZOS)
    return Image.alpha_composite(im, cue)

def changed_pixel_count(diff: Image.Image) -> int:
    return sum(1 for p in diff.getdata() if p != (0, 0, 0, 0))

def composite(character: Image.Image) -> Image.Image:
    drum = Image.open(DRUM).convert("RGBA")
    if drum.size != character.size:
        raise SystemExit(f"drum size mismatch: {drum.size} vs {character.size}")
    merged = Image.alpha_composite(drum, character)
    white = Image.new("RGBA", merged.size, (255, 255, 255, 255))
    return Image.alpha_composite(white, merged)

OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)

result = {
    "schemaVersion": 1,
    "actionKey": "BD+RC+SN:RF/R/L",
    "method": "formal RC+SN:R/L exact bytes + proven deterministic BD cue only",
    "phases": {},
}

allowed = (438, 778, 510, 836)

for phase, (src, expected_sha) in PARENTS.items():
    actual = sha256(src)
    if actual != expected_sha:
        raise SystemExit(f"{phase} source SHA mismatch: {actual} != {expected_sha}")

    base = Image.open(src).convert("RGBA")
    if base.size != (1448, 1086):
        raise SystemExit(f"{phase} source size mismatch: {base.size}")

    candidate = add_proven_bd_cue(base.copy(), phase)
    out = OUT / f"bd_rc_sn_rf_r_l_{phase}_attempt01.png"
    candidate.save(out, optimize=False)

    diff = ImageChops.difference(base, candidate)
    bbox = diff.getbbox()
    changed = changed_pixel_count(diff)
    ratio = changed / (base.width * base.height)

    if bbox is None:
        raise SystemExit(f"{phase}: deterministic cue made no change")
    if not (bbox[0] >= allowed[0] and bbox[1] >= allowed[1] and bbox[2] <= allowed[2] and bbox[3] <= allowed[3]):
        raise SystemExit(f"{phase}: change escaped allowed BD-cue region: {bbox}")

    comp = composite(candidate)
    comp_path = QA / f"bd_rc_sn_rf_r_l_{phase}_fixed_drum.png"
    comp.save(comp_path)

    result["phases"][phase] = {
        "parentPath": str(src.relative_to(ROOT)),
        "parentSha256": expected_sha,
        "candidatePath": str(out.relative_to(ROOT)),
        "candidateSha256": sha256(out),
        "width": candidate.width,
        "height": candidate.height,
        "mode": candidate.mode,
        "changedPixels": changed,
        "changedPixelRatio": ratio,
        "diffBBox": bbox,
        "locality": "PASS_BD_CUE_ONLY",
        "compositePath": str(comp_path.relative_to(ROOT)),
    }

(QA / "build-result.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False, indent=2))
