#!/usr/bin/env python3
"""Validate fixed-canvas layer registration and animation config references."""

from __future__ import annotations
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "character-assets"
CONFIG = ASSETS / "config"


def main() -> int:
    manifest = json.loads((CONFIG / "layer_manifest.json").read_text(encoding="utf-8"))
    rules = json.loads((CONFIG / "animation_rules.json").read_text(encoding="utf-8"))
    size = (manifest["canvas"]["width"], manifest["canvas"]["height"])
    errors = []

    if manifest["registration"] != {
        "x": 0, "y": 0, "allowTranslation": False,
        "allowScale": False, "allowMirror": False, "allowCrop": False
    }:
        errors.append("registration must remain fully locked at x=0,y=0")

    for path in (ASSETS / "layers").rglob("*.png") if (ASSETS / "layers").exists() else []:
        try:
            with Image.open(path) as img:
                if img.size != size:
                    errors.append(f"{path.relative_to(ROOT)}: {img.size} != {size}")
                if img.mode not in ("RGBA", "LA", "P"):
                    errors.append(f"{path.relative_to(ROOT)}: expected transparency-capable PNG mode, got {img.mode}")
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    # Validate frame naming syntax even before all binary layers exist.
    for part, by_rate in rules.get("parts", {}).items():
        for rate, rule in by_rate.items():
            for frame in rule.get("frames", []):
                if "/" not in frame:
                    errors.append(f"{part}.{rate}: invalid frame id {frame!r}")

    if errors:
        print("Character asset validation failed:")
        for e in errors:
            print(f"- {e}")
        return 1

    print(f"Character asset validation OK. Canvas={size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
