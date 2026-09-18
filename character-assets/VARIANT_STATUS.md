# Character Variant Status

## Persistent visual QA ledger — 2026-09-18

All current and future character-pose visual defects are tracked in:
- `prototypes/luna_say_maybe_16m/CHARACTER_QA_ISSUES.json`
- `prototypes/luna_say_maybe_16m/CHARACTER_QA_WORKFLOW.md`

Every new chat/session must read the ledger before editing character assets. Completed items remain in the ledger as `DONE`; unnecessary items become `WONT_FIX` with a reason. Do not treat an asset as visually approved merely because manifest/runtime validation passes.


## Authoritative state — 2026-09-18

Active prototype scope: **Luna Say Maybe measures 1-4**.

GitHub `main` currently contains the complete 1-4 runtime frame set referenced by the inventory:
- `layers/character/base/neutral.png`
- `layers/character/sn/hit_l.png`
- `layers/character/sn/rebound_l.png`
- `layers/character/sn/hit_r.png`
- `layers/character/sn/rebound_r.png`
- `layers/character/hh/hit_r.png`
- `layers/character/hh/rebound_r.png`
- `layers/character/bd/hit_rf.png`
- `layers/character/bd/rebound_rf.png`
- `layers/character/combo/bd_rc_hit.png`
- `layers/character/combo/bd_rc_rebound.png`

Runtime action keys:
- `SN:L`
- `SN:R`
- `HH:R`
- `BD:RF`
- `BD+RC:*`

Runtime scope is 28 notes / 27 groups. The temporary 1-16 runtime change was rolled back; `site/character-prototype.js` and `asset_inventory.json` are aligned on measures 1-4.

Limb data remains authoritative:
- `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json`
- `site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json`

## Fixed neutral and drum — 2026-09-18
The current-chat attached PNGs are the authoritative fixed layers and were imported byte-for-byte after PNG, canvas, alpha, and SHA verification.

Neutral runtime path: `layers/character/base/neutral.png`  
Neutral SHA-256: `886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`  
Semantic role: `initial-neutral-home-ready-pose`  
Status: `APPROVED_FIXED`

Drum runtime path: `layers/drum/drum_base.png`  
Drum SHA-256: `dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85`  
Status: `APPROVED_FIXED`

Both canvases are 1448x1086. The runtime stack is drum behind character, with matching canvas registration and no per-layer translation or independent scale.

## Later-measure assets
Additional historical 1-16 character PNGs may still exist in the repository tree, but they are outside the active refreshed 1-4 visual scope and must not be treated as newly approved for expansion without explicit review.
