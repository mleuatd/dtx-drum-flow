#!/usr/bin/env python3
"""Prepare one 2-action / 4-frame visual-integrity QA batch from latest checkout.

Reads BRUSHUP_LEDGER.json, selects the next two action keys by project priority,
verifies formal PNG SHA-256/canvas/alpha, and emits full-resolution character-only,
fixed-drum composite, and transition-strip evidence plus a machine-readable manifest.
Does not mutate formal PNGs or ledgers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json"
DRUM = ROOT / "character-assets/layers/drum/drum_base.png"
NEUTRAL = ROOT / "character-assets/layers/character/base/neutral.png"

PRIORITY = [
    "NEEDS_HUMAN_ANATOMY_QA",
    "NEEDS_LINEWORK_QA",
    "NEEDS_FIXED_DRUM_COMPOSITE_QA",
    "NEEDS_VISUAL_REVIEW",
    "IN_FIX",
    "CLAIMED_RETRYING",
    "PENDING",
    "NEEDS_RUNTIME_TRANSITION_QA",
]
TERMINAL_STATUSES = {
    "VERIFIED", "APPROVED_LIVE", "HOLD_VISUAL_INTEGRITY", "REJECTED", "BLOCKED"
}
CANVAS = (1448, 1086)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def open_rgba(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    if im.size != CANVAS:
        raise ValueError(f"{path}: expected {CANVAS}, got {im.size}")
    return im


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


def rank(status: str) -> int:
    try:
        return PRIORITY.index(status)
    except ValueError:
        return 999


def select_targets(data: dict[str, Any], action_keys: list[str] | None) -> list[dict[str, Any]]:
    targets = data["targets"]
    if action_keys:
        chosen = [t for t in targets if t.get("actionKey") in action_keys and t.get("phase") in {"hit", "rebound"}]
        found = {t.get("actionKey") for t in chosen}
        missing = [x for x in action_keys if x not in found]
        if missing:
            raise SystemExit(f"action keys not found in ledger: {missing}")
        return sorted(chosen, key=lambda t: (action_keys.index(t["actionKey"]), 0 if t["phase"] == "hit" else 1))

    # On push-triggered runs, honor the explicit batch already CLAIMED in the ledger.
    # This prevents auto-priority selection from stealing work owned by another parallel session.
    active = data.get("activeVisualIntegrityBatch") or {}
    active_keys = active.get("actionKeys") or []
    active_batch_id = active.get("batchId")
    if len(active_keys) in {1, 2} and active_batch_id:
        claimed = [
            t for t in targets
            if t.get("actionKey") in active_keys
            and t.get("phase") in {"hit", "rebound"}
            and t.get("reviewClaimState") == "CLAIMED"
            and t.get("activeReviewBatchId") == active_batch_id
        ]
        found = {t.get("actionKey") for t in claimed}
        phases_by_key = {
            key: {t.get("phase") for t in claimed if t.get("actionKey") == key}
            for key in active_keys
        }
        if found == set(active_keys) and all({"hit", "rebound"}.issubset(phases_by_key[key]) for key in active_keys):
            return sorted(claimed, key=lambda t: (active_keys.index(t["actionKey"]), 0 if t["phase"] == "hit" else 1))

    grouped: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for t in sorted(targets, key=lambda x: x.get("order", 999999)):
        if t.get("phase") not in {"hit", "rebound"}:
            continue
        st = t.get("brushupStatus", "")
        if st in TERMINAL_STATUSES:
            continue
        grouped.setdefault(t.get("actionKey", ""), []).append(t)

    candidates = []
    for key, group in grouped.items():
        phases = {x.get("phase") for x in group}
        if {"hit", "rebound"}.issubset(phases):
            best = min(rank(x.get("brushupStatus", "")) for x in group)
            first_order = min(x.get("order", 999999) for x in group)
            candidates.append((best, first_order, key, group))
    candidates.sort(key=lambda x: (x[0], x[1]))
    keys = [x[2] for x in candidates[:2]]
    if len(keys) < 2:
        raise SystemExit("fewer than two eligible action keys remain")
    chosen = [t for t in targets if t.get("actionKey") in keys and t.get("phase") in {"hit", "rebound"}]
    return sorted(chosen, key=lambda t: (keys.index(t["actionKey"]), 0 if t["phase"] == "hit" else 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="visual-qa/batch")
    ap.add_argument("--actions", help="comma-separated action keys; omit for automatic priority selection")
    args = ap.parse_args()

    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    requested = [x.strip() for x in args.actions.split(",") if x.strip()] if args.actions else None
    if requested and len(requested) not in {1, 2}:
        raise SystemExit("--actions must contain one or two action keys")
    targets = select_targets(data, requested)
    action_keys = list(OrderedDict.fromkeys(t["actionKey"] for t in targets))
    if len(action_keys) not in {1, 2} or len(targets) != len(action_keys) * 2:
        raise SystemExit(f"expected 1-2 actions / 2 frames each, got {len(action_keys)} / {len(targets)}")

    out = ROOT / args.out
    chars = out / "character_only"
    comps = out / "fixed_drum_composites"
    strips = out / "transition_strips"
    for p in (chars, comps, strips):
        p.mkdir(parents=True, exist_ok=True)

    drum = open_rgba(DRUM)
    neutral = open_rgba(NEUTRAL)
    manifest: dict[str, Any] = {
        "schemaVersion": 1,
        "ledgerUpdatedAt": data.get("updatedAt"),
        "selectionMode": "explicit" if requested else ("active-claimed-batch" if (data.get("activeVisualIntegrityBatch") or {}).get("actionKeys") == action_keys else "auto-priority"),
        "actionKeys": action_keys,
        "canvas": list(CANVAS),
        "registration": {"x": 0, "y": 0, "scale": 1},
        "drum": {"path": str(DRUM.relative_to(ROOT)), "sha256": sha256(DRUM)},
        "neutral": {"path": str(NEUTRAL.relative_to(ROOT)), "sha256": sha256(NEUTRAL)},
        "frames": [],
    }

    loaded: dict[tuple[str, str], Image.Image] = {}
    for t in targets:
        p = ROOT / t["formalGitHubPath"]
        actual_sha = sha256(p)
        expected_sha = t.get("sha256")
        if expected_sha and actual_sha != expected_sha:
            raise SystemExit(f"SHA mismatch for {p}: ledger={expected_sha} actual={actual_sha}")
        ch = open_rgba(p)
        loaded[(t["actionKey"], t["phase"])] = ch
        label = f'{t["actionKey"]} {t["phase"]}'
        s = slug(label)
        bg = Image.new("RGBA", CANVAS, (250, 250, 250, 255))
        Image.alpha_composite(bg, ch).save(chars / f"{s}.png")
        comp = Image.alpha_composite(drum, ch)
        Image.alpha_composite(bg, comp).save(comps / f"{s}.png")
        manifest["frames"].append({
            "id": t.get("id"), "actionKey": t["actionKey"], "phase": t["phase"],
            "status": t.get("brushupStatus"), "qaState": t.get("qaState"),
            "formalGitHubPath": t["formalGitHubPath"], "sha256": actual_sha,
            "alphaBBox": list(ch.getchannel("A").getbbox() or []),
        })

    for key in action_keys:
        seq = [("neutral_before", neutral), ("hit", loaded[(key, "hit")]),
               ("rebound", loaded[(key, "rebound")]), ("neutral_after", neutral)]
        thumb = (362, 272)
        label_h = 28
        strip = Image.new("RGB", (thumb[0] * 4, thumb[1] + label_h), (238, 238, 238))
        draw = ImageDraw.Draw(strip)
        for i, (lab, ch) in enumerate(seq):
            comp = Image.alpha_composite(drum, ch)
            bg = Image.new("RGBA", CANVAS, (250, 250, 250, 255))
            panel = Image.alpha_composite(bg, comp).convert("RGB").resize(thumb, Image.Resampling.LANCZOS)
            strip.paste(panel, (i * thumb[0], label_h))
            draw.text((i * thumb[0] + 8, 6), lab, fill=(0, 0, 0))
        strip.save(strips / f"{slug(key)}_neutral_hit_rebound_neutral.png")

    (out / "batch_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"actionKeys": action_keys, "frames": len(targets), "out": str(out.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
