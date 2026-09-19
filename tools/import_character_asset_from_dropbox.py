#!/usr/bin/env python3
import argparse, hashlib, json, os, pathlib, urllib.request
from PIL import Image

ROOT = pathlib.Path(".")
MANIFEST = ROOT / "character-assets/config/assets_manifest.json"
INVENTORY = ROOT / "character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json"
REQ_M1_4 = ROOT / "character-assets/prototypes/luna_say_maybe_16m/M1_4_REQUIRED_CHARACTER_ASSETS.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def download(stage):
    token = os.environ.get("DROPBOX_ACCESS_TOKEN")
    if token:
        req = urllib.request.Request(
            "https://content.dropboxapi.com/2/files/download",
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Dropbox-API-Arg": json.dumps({"path": stage["dropboxPath"]}),
            },
        )
    else:
        url = stage.get("downloadUrl")
        if not url:
            raise SystemExit("DROPBOX_ACCESS_TOKEN secret or staging downloadUrl is required")
        req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as r:
        return r.read()

def verify_png(raw, width, height):
    tmp = pathlib.Path("/tmp/dropbox_source.png")
    tmp.write_bytes(raw)
    im = Image.open(tmp)
    if im.format != "PNG":
        raise SystemExit("source is not PNG")
    if im.size != (width, height):
        raise SystemExit(f"exact-byte import requires {(width,height)}, got {im.size}")
    rgba = im.convert("RGBA")
    if rgba.getchannel("A").getextrema()[0] >= 255:
        raise SystemExit("image has no transparency")

def update_metadata(stage):
    key = stage["assetKey"]
    sha = stage["sha256"]
    github_path = stage["githubPath"]
    fixed = key in {"neutral", "drum_base"}
    fixed_status = "APPROVED_FIXED" if fixed else "READY"

    manifest = load(MANIFEST)
    for a in manifest.get("assets", []):
        if a.get("path") == github_path:
            a.update({
                "sha256": sha,
                "width": stage["width"],
                "height": stage["height"],
                "part": stage["part"],
                "phase": stage["phase"],
                "hand": stage.get("limb"),
                "status": fixed_status,
            })
            break
    else:
        manifest.setdefault("assets", []).append({
            "path": github_path,
            "width": stage["width"], "height": stage["height"], "x": 0, "y": 0,
            "sha256": sha, "status": fixed_status,
            "purpose": "Luna character runtime asset",
            "part": stage["part"], "phase": stage["phase"], "hand": stage.get("limb"), "notes": []
        })
    if key == "neutral":
        manifest["lockedNeutralSha256"] = sha
    if key == "drum_base":
        manifest["lockedDrumSha256"] = sha
    save(MANIFEST, manifest)

    inv = load(INVENTORY)
    rel = github_path.removeprefix("character-assets/")
    if key != "drum_base":
        inv.setdefault("requiredFrames", {}).setdefault(key, {}).update({"path": rel, "state": "ready", "sha256": sha})
        runtime_key = stage.get("runtimeKey")
        if runtime_key:
            inv.setdefault("runtimePhaseFrameMap", {}).setdefault(runtime_key, {})[stage["phase"]] = key
            if stage["phase"] == "hit":
                inv.setdefault("runtimeFrameMap", {})[runtime_key] = key
    else:
        inv.setdefault("qa", {})["fixedDrumSha256"] = sha
    save(INVENTORY, inv)

    if REQ_M1_4.exists():
        req = load(REQ_M1_4)
        changed = False
        for item in req.get("assets", []):
            if item.get("requiredAssetKey") == key:
                item.update({
                    "status": "READY_GITHUB",
                    "sha256": sha,
                    "width": stage["width"],
                    "height": stage["height"],
                    "dropboxPath": stage["dropboxPath"],
                })
                changed = True
                break
        if changed:
            save(REQ_M1_4, req)

def process(stage_path):
    stage_path = pathlib.Path(stage_path)
    stage = load(stage_path)
    if stage.get("status") == "IMPORTED":
        print(f"{stage_path}: already imported")
        return False

    raw = download(stage)
    source_sha = hashlib.sha256(raw).hexdigest()
    expected_source = stage["sourceSha256"].lower()
    expected_final = stage["sha256"].lower()
    if source_sha != expected_source:
        raise SystemExit(f"{stage_path}: source sha mismatch {source_sha} != {expected_source}")

    width, height = int(stage["width"]), int(stage["height"])
    verify_png(raw, width, height)

    if (stage.get("schemaVersion") or 1) >= 2 and expected_source != expected_final:
        raise SystemExit(f"{stage_path}: schemaVersion 2 forbids normalization/re-encoding")

    target = pathlib.Path(stage["githubPath"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    final_sha = hashlib.sha256(target.read_bytes()).hexdigest()
    if final_sha != expected_final:
        raise SystemExit(f"{stage_path}: final sha mismatch {final_sha} != {expected_final}")

    update_metadata(stage)
    stage["status"] = "IMPORTED"
    stage["importedSha256"] = final_sha
    stage.pop("downloadUrl", None)
    save(stage_path, stage)
    print(json.dumps({"stage": str(stage_path), "githubPath": str(target), "sha256": final_sha, "status": "IMPORTED"}))
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("staging", nargs="+")
    args = ap.parse_args()
    any_change = False
    for p in args.staging:
        any_change = process(p) or any_change
    print(json.dumps({"processed": len(args.staging), "changed": any_change}))

if __name__ == "__main__":
    main()
