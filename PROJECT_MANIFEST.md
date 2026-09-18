# DTX Drum Flow — Shared Project Manifest

## Current highest-priority task — 2026-09-18
Continue the refreshed Luna Say Maybe character flipbook from **measure 5 onward**, while preserving the completed measures 1-4 visual baseline.

Current recovery/state files:
- `character-assets/prototypes/luna_say_maybe_16m/CHARACTER_QA_ISSUES.json`
- `character-assets/prototypes/luna_say_maybe_16m/M5_8_REQUIRED_CHARACTER_ASSETS.json`
- `character-assets/prototypes/luna_say_maybe_16m/M9_16_REQUIRED_CHARACTER_ASSETS.json`
- `character-assets/VARIANT_STATUS.md`

## Current coherent runtime state
- Live refreshed runtime scope remains measures 1-4 until later-measure frames pass the same QA.
- `site/character-prototype.js`: `PROTOTYPE_MEASURE_END=4`
- `asset_inventory.json`: measures 1-4 / 28 notes / 27 groups
- Current approved action keys: `SN:L`, `SN:R`, `HH:R`, `BD:RF`, `BD+RC:*`
- Measures 5-16 have been recomputed from FINAL notes + authoritative 1-16 limb metadata, but have not been wired with rejected historical images.

## Refreshed expansion preparation
### Measures 5-8
- 33 notes / 32 groups.
- New key: `RD:R`.
- Required new current-baseline frames: RD:R hit + rebound.
- Historical `rd/hit_r.png` rejected by visual QA run `35315598184`, artifact `10535695236`.

### Measures 9-16
- 83 notes / 65 groups / limb missing = 0.
- New current-baseline keys: `RD:R`, `BD+SN:RF/L`, `RC+SN:L/R`.
- Required new frames across measures 5-16: six total (RD hit/rebound, BD+SN hit/rebound, RC+SN hit/rebound).
- Historical BD+SN and RC+SN hit PNGs rejected by visual QA run `35315877548`, artifact `10535690785`.

### Measures 17-148
- FINAL chart: 2,014 notes after measure 16; last measure 148.
- No embedded limb/hand/foot metadata exists in those 2,014 notes.
- The only precomputed authoritative limb sidecar currently in GitHub covers measures 1-16.
- Do not invent measure 17+ hand/foot assignments. Create and validate an authoritative full-song limb sidecar before refreshed runtime mapping continues beyond measure 16.

## Character image state
GitHub `main` contains the fixed neutral plus 10 refreshed M1-4 hit/rebound variants. Historical later-measure PNGs remain in the tree only as history/candidates and are not approved automatically.

Approved fixed neutral:
- `character-assets/layers/character/base/neutral.png`
- SHA-256 `886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`
- 1448x1086 RGBA, x=0/y=0

## Fixed drum state
Approved fixed drum:
- `character-assets/layers/drum/drum_base.png`
- SHA-256 `dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85`
- 1448x1086 RGBA, x=0/y=0

The drum is immutable for character-pose work. Do not regenerate, move, rescale, or replace it when creating character variants.

## Current image-creation blocker
The exact approved neutral is recoverable from GitHub QA artifacts for inspection, but the image-editing interface available in the current normal-chat workflow cannot consume that repository/artifact binary as a direct edit target. Since refreshed variants must be direct edits of the approved baseline and a look-alike redraw is forbidden, later-measure image creation is explicitly BLOCKED rather than lowering consistency.

## Canonical site
- GitHub repository: https://github.com/mleuatd/dtx-drum-flow
- Default branch: main
- GitHub Pages: https://mleuatd.github.io/dtx-drum-flow/

## Fixed registration
- canvas: 1448x1086
- registration: x=0,y=0
- fixed drum + separate character + optional effects
- validation: `tools/character_layers/validate_assets.py`

## Historical context
Older full-song/1-16/1-8 runtime experiments remain in Git history. They are not the active refreshed visual scope and must not override the current manifests, QA ledger, or user-approved M1-4 baseline.
