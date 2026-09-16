#!/usr/bin/env python3
"""Composite DTX Drum Flow character layers without changing registration."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "character-assets"
CONFIG = ASSETS / "config"


def load_manifest():
    return json.loads((CONFIG / "layer_manifest.json").read_text(encoding="utf-8"))


def open_layer(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    if img.size != size:
        raise ValueError(f"{path}: expected {size[0]}x{size[1]}, got {img.size[0]}x{img.size[1]}")
    return img


def resolve_character(frame: str) -> Path:
    # frame format example: hh/hit_r
    part, pose = frame.split("/", 1)
    return ASSETS / "layers" / "character" / part / f"{pose}.png"


def compose(frame: str, output: Path, effect: str | None = None) -> None:
    manifest = load_manifest()
    size = (manifest["canvas"]["width"], manifest["canvas"]["height"])
    if manifest["registration"]["x"] != 0 or manifest["registration"]["y"] != 0:
        raise ValueError("Non-zero registration is forbidden")

    drum = open_layer(ASSETS / "layers" / "drum" / "drum_base.png", size)
    character = open_layer(resolve_character(frame), size)

    out = Image.new("RGBA", size, (255, 255, 255, 0))
    out.alpha_composite(drum, (0, 0))
    out.alpha_composite(character, (0, 0))

    if effect:
        effect_path = ASSETS / "layers" / "effect" / f"{effect}.png"
        out.alpha_composite(open_layer(effect_path, size), (0, 0))

    output.parent.mkdir(parents=True, exist_ok=True)
    out.save(output)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frame", help="character frame, e.g. hh/hit_r")
    ap.add_argument("output", type=Path)
    ap.add_argument("--effect")
    args = ap.parse_args()
    compose(args.frame, args.output, args.effect)


if __name__ == "__main__":
    main()
