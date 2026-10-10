# DTX Drum Flow — Shared Project Manifest

## CURRENT AUTHORITY — 2026-09-21

Character-image repair is temporarily operating in **ONE_IMAGE_ONLY** mode.

Read first:
- `character-assets/versions/one-by-one-qa/CURRENT_STATUS.json`
- `character-assets/versions/one-by-one-qa/README.md`

Active case:
- DMR-009
- `combo/bd_hh_rf_r_hit_refresh.png`
- status: RETRY_REQUIRED / promotion blocked
- do not advance to a second image during this experiment

The previous DMR-009 contact recheck remains evidence, not current-state authority:
- `character-assets/versions/donor-mesh-v3/qa/dmr009_contact_reqa_20260921.json`

Diagnostic order is now registration-first:
global/static registration -> torso registration -> active limb geometry -> contact -> fixed-drum composite -> transition.

The sections below are retained as historical project context. When they conflict with the CURRENT AUTHORITY section above, the one-by-one current status wins.

## Historical highest-priority task — 2026-09-18
Continue the refreshed Luna Say Maybe character flipbook from measure 5 onward without changing the completed measures 1-4 baseline.

Historical read-first files:
- `character-assets/prototypes/luna_say_maybe_16m/M5_PLUS_PROGRESS_LEDGER.json`
- `character-assets/prototypes/luna_say_maybe_16m/HANDOFF_M5_PLUS_2026-09-18.md`
- `character-assets/prototypes/luna_say_maybe_16m/CHARACTER_QA_ISSUES.json`

## Historical live-runtime snapshot
- Public refreshed scope: measures 1-4.
- Scope source: `character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json`.
- `site/character-prototype.js` reads `inventory.runtimeScope`.
- Snapshot inventory scope: 28 notes / 27 groups, keys `SN:L`, `SN:R`, `HH:R`, `BD:RF`, `BD+RC:*`.
- Inventory-scope refactor live QA: run `35321917979`, artifact `10536838661`, success.

## Fixed baseline
Neutral:
- `character-assets/layers/character/base/neutral.png`
- SHA-256 `886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`
- 1448x1086 RGBA, x=0/y=0

Fixed drum:
- `character-assets/layers/drum/drum_base.png`
- SHA-256 `dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85`
- 1448x1086 RGBA, x=0/y=0

Do not move, mirror, regenerate, rescale, or overwrite these fixed layers during character work.

## Historical measures 5-8
- 33 notes / 32 groups, limb missing 0.
- Keys: BD:RF, RD:R, SN:L, BD+RC:*.
- Historical blocker: refreshed RD:R hit/rebound.

## Historical measures 9-16
- 83 notes / 65 groups, limb missing 0.
- Additional keys: RD:R, BD+SN:RF/L, RC+SN:L/R.
- Refreshed BD+SN hit/rebound were preserved at:
  - `character-assets/layers/character/combo/bd_sn_hit_refresh.png`
  - `character-assets/layers/character/combo/bd_sn_rebound_refresh.png`

## Measures 17-148 reference
FINAL chart after measure 16:
- 2,014 notes
- 1,403 time groups
- last measure 148

## Canonical repository/site
- Repository: https://github.com/mleuatd/dtx-drum-flow
- Branch: main
- GitHub Pages: https://mleuatd.github.io/dtx-drum-flow/
