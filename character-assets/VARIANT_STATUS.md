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


## Refreshed expansion status — 2026-09-18

The refreshed visual runtime remains **measures 1-4 only** until later-measure frames pass the same visual/runtime QA standard. Expansion analysis has now been completed for measures 5-16 without changing the live mapping.

### Measures 5-8
Authoritative coverage from FINAL notes + 1-16 limb sidecar:
- 33 notes / 32 time groups
- keys: `BD:RF`, `RD:R`, `SN:L`, `BD+RC:*`
- approved M1-4 reuse: BD, SN:L, BD+RC
- new refreshed frames required: `RD:R hit` + `RD:R rebound`

The historical `layers/character/rd/hit_r.png` was visually compared against the current fixed drum + refreshed M1-4 baseline in GitHub Actions run `35315598184`, artifact `10535695236`, and was rejected. It is a different/shifted drawing family and must not be used.

Definition:
`prototypes/luna_say_maybe_16m/M5_8_REQUIRED_CHARACTER_ASSETS.json`

### Measures 9-16
Authoritative coverage:
- 83 notes / 65 time groups / missing limb assignments 0
- group keys include `BD:RF`, `RD:R`, `SN:L`, `BD+RC`, `HH:R`, `BD+SN:RF/L`, `RC+SN:L/R`
- new refreshed frames beyond the M1-4 set: RD hit/rebound, BD+SN hit/rebound, RC+SN hit/rebound

Historical `bd_sn_hit.png` and `rc_sn_hit.png` were visually compared in GitHub Actions run `35315877548`, artifact `10535690785`, and rejected for the same baseline mismatch. No refreshed rebound frames exist.

Definition:
`prototypes/luna_say_maybe_16m/M9_16_REQUIRED_CHARACTER_ASSETS.json`

### Measures 17-148
The FINAL chart contains 2,014 notes after measure 16 through measure 148. None carries embedded limb/hand/foot metadata. The only precomputed authoritative limb assignment currently in GitHub is `Luna_say_maybe_1_16_limbs.json`.

`hand_rules.json` exists, but it is a rule specification scoped to the 1-16 prototype, not a per-note full-song authoritative sidecar. Do not guess hands/feet for measure 17+ runtime mapping. A full-song limb sidecar must be generated/validated and made authoritative before refreshed visual mapping continues past measure 16.

### Current blocker
The exact approved neutral can be recovered and visually inspected from GitHub QA artifacts, but the image-editing interface available in this normal-chat workflow cannot take that repository/artifact PNG as a direct edit target. Because project rules forbid a fresh look-alike redraw, the six required refreshed frames for measures 5-16 are left BLOCKED rather than generating an inconsistent character.

Tracked issues:
- `CHAR-QA-0005`: RD:R refreshed hit/rebound
- `CHAR-QA-0006`: BD+SN and RC+SN refreshed hit/rebound
