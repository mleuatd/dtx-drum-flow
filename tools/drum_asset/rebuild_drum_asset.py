from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "tools" / "drum_asset"
MANIFEST_PATH = SOURCE_DIR / "drum_base_manifest.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    target = ROOT / manifest["target"]
    expected_sha = manifest["sha256"]
    expected_size = int(manifest["byte_size"])
    expected_dimensions = tuple(manifest["dimensions"])

    chunks: list[str] = []
    for part_name in manifest["parts"]:
        part_path = SOURCE_DIR / part_name
        part = json.loads(part_path.read_text(encoding="utf-8"))
        chunks.append(part["base64"])

    data = base64.b64decode("".join(chunks), validate=True)
    actual_sha = sha256_bytes(data)
    if len(data) != expected_size:
        raise SystemExit(f"byte size mismatch: {len(data)} != {expected_size}")
    if actual_sha != expected_sha:
        raise SystemExit(f"sha256 mismatch: {actual_sha} != {expected_sha}")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)

    with Image.open(target) as image:
        if image.format != "PNG":
            raise SystemExit(f"not PNG: {image.format}")
        if tuple(image.size) != expected_dimensions:
            raise SystemExit(f"dimension mismatch: {image.size} != {expected_dimensions}")
        rgba = image.convert("RGBA")
        amin, amax = rgba.getchannel("A").getextrema()
        if amin != 0 or amax != 255:
            raise SystemExit(f"alpha range mismatch: {amin}..{amax}")

    # Lock active metadata to the exact rebuilt binary.
    assets_manifest_path = ROOT / "character-assets" / "config" / "assets_manifest.json"
    assets_manifest = json.loads(assets_manifest_path.read_text(encoding="utf-8"))
    assets_manifest["lockedDrumSha256"] = actual_sha
    for item in assets_manifest.get("assets", []):
        if item.get("path") == manifest["target"]:
            item["sha256"] = actual_sha
            item["width"], item["height"] = expected_dimensions
            item["ready"] = True
            break
    else:
        raise SystemExit("drum asset entry not found in assets_manifest.json")
    write_json(assets_manifest_path, assets_manifest)

    inventory_path = ROOT / "character-assets" / "prototypes" / "luna_say_maybe_16m" / "asset_inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory.setdefault("qa", {})["fixedDrumSha256"] = actual_sha
    write_json(inventory_path, inventory)

    print(f"rebuilt {manifest['target']}")
    print(f"bytes={len(data)}")
    print(f"sha256={actual_sha}")


if __name__ == "__main__":
    main()
