#!/usr/bin/env python3
"""Validate fixed-canvas layer registration and animation config references."""

from __future__ import annotations
import json
import hashlib
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "character-assets"
CONFIG = ASSETS / "config"
PROTOTYPE = ASSETS / "prototypes" / "luna_say_maybe_16m"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads((CONFIG / "layer_manifest.json").read_text(encoding="utf-8"))
    assets_manifest = json.loads((CONFIG / "assets_manifest.json").read_text(encoding="utf-8"))
    rules = json.loads((CONFIG / "animation_rules.json").read_text(encoding="utf-8"))
    inventory = json.loads((PROTOTYPE / "asset_inventory.json").read_text(encoding="utf-8"))
    size = (manifest["canvas"]["width"], manifest["canvas"]["height"])
    errors = []

    if manifest["registration"] != {
        "x": 0, "y": 0, "allowTranslation": False,
        "allowScale": False, "allowMirror": False, "allowCrop": False
    }:
        errors.append("registration must remain fully locked at x=0,y=0")

    listed_paths = set()
    for asset in assets_manifest.get("assets", []):
        relative = asset.get("path", "")
        if relative in listed_paths:
            errors.append(f"assets_manifest: duplicate path {relative}")
            continue
        listed_paths.add(relative)
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"assets_manifest: missing file {relative}")
            continue
        try:
            with Image.open(path) as img:
                expected_size = (asset.get("width"), asset.get("height"))
                if img.format != "PNG":
                    errors.append(f"{relative}: expected PNG, got {img.format}")
                if img.size != size or img.size != expected_size:
                    errors.append(f"{relative}: {img.size} != fixed/manifest size {size}/{expected_size}")
                if (asset.get("x"), asset.get("y")) != (0, 0):
                    errors.append(f"{relative}: registration must be x=0,y=0")
                alpha = img.convert("RGBA").getchannel("A")
                alpha_min, alpha_max = alpha.getextrema()
                if alpha_min == 255:
                    errors.append(f"{relative}: no transparent pixels")
                if alpha_max == 0:
                    errors.append(f"{relative}: layer is fully transparent")
        except Exception as exc:
            errors.append(f"{relative}: {exc}")
            continue

        actual_sha = sha256(path)
        if actual_sha != asset.get("sha256"):
            errors.append(f"{relative}: SHA-256 {actual_sha} != manifest {asset.get('sha256')}")

    actual_paths = {
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ASSETS / "layers").rglob("*.png")
    }
    for relative in sorted(actual_paths - listed_paths):
        errors.append(f"assets_manifest: unregistered PNG {relative}")
    for relative in sorted(listed_paths - actual_paths):
        errors.append(f"assets_manifest: path outside current layer set or missing {relative}")

    drum_path = "character-assets/layers/drum/drum_base.png"
    locked_drum_sha = assets_manifest.get("lockedDrumSha256")
    drum_entry = next((a for a in assets_manifest.get("assets", []) if a.get("path") == drum_path), None)
    if not drum_entry or drum_entry.get("sha256") != locked_drum_sha:
        errors.append("lockedDrumSha256 must match the drum_base.png manifest entry")

    required = inventory.get("requiredFrames", {})
    for frame_id, frame in required.items():
        relative = "character-assets/" + frame.get("path", "")
        if relative not in listed_paths:
            errors.append(f"asset_inventory {frame_id}: unregistered or missing {relative}")
        entry = next((a for a in assets_manifest.get("assets", []) if a.get("path") == relative), None)
        if entry and frame.get("sha256") != entry.get("sha256"):
            errors.append(f"asset_inventory {frame_id}: SHA-256 does not match assets_manifest")

    animation = json.loads(
        (PROTOTYPE / "Luna_say_maybe_16m_animation.json").read_text(encoding="utf-8")
    )
    notes = animation.get("notes", [])
    if len(notes) != inventory.get("chartNoteCount"):
        errors.append(
            f"prototype note count {len(notes)} != inventory {inventory.get('chartNoteCount')}"
        )
    groups = []
    for note in notes:
        if groups and abs(note["time"] - groups[-1][0]["time"]) <= 0.008:
            groups[-1].append(note)
        else:
            groups.append([note])
    frame_map = inventory.get("runtimeFrameMap", {})
    for group in groups:
        parts = sorted({note["part"] for note in group})
        if len(parts) > 1:
            key = "+".join(parts) + ":*"
        else:
            hand = group[0].get("animation", {}).get("hand", "R")
            key = f"{parts[0]}:{hand}"
        frame_id = frame_map.get(key)
        if not frame_id or frame_id not in required:
            errors.append(
                f"prototype time {group[0]['time']}: unresolved animation key {key}"
            )

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

    print(
        f"Character asset validation OK. Canvas={size[0]}x{size[1]}, "
        f"registered PNGs={len(listed_paths)}, prototype frames={len(required)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
