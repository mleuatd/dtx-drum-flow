# DTX Drum Flow — Shared Project Manifest

## Current highest-priority task — 2026-09-18
Continue the refreshed Luna Say Maybe character flipbook from measure 5 onward without changing the completed measures 1-4 baseline.

Read first:
- `character-assets/prototypes/luna_say_maybe_16m/M5_PLUS_PROGRESS_LEDGER.json`
- `character-assets/prototypes/luna_say_maybe_16m/HANDOFF_M5_PLUS_2026-09-18.md`
- `character-assets/prototypes/luna_say_maybe_16m/CHARACTER_QA_ISSUES.json`

## Current live runtime
- Public refreshed scope: measures 1-4.
- Scope source: `character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json`.
- `site/character-prototype.js` now reads `inventory.runtimeScope`; it no longer hardcodes measure 4.
- Current inventory scope: 28 notes / 27 groups, keys `SN:L`, `SN:R`, `HH:R`, `BD:RF`, `BD+RC:*`.
- Inventory-scope refactor live QA: run `35321917979`, artifact `10536838661`, success.
- General validate: success.
- Character asset validation: success after allowing extra runtime-pending later-measure layers while keeping the active M1-4 set separately validated.

## Fixed baseline
Neutral:
- `character-assets/layers/character/base/neutral.png`
- SHA-256 `886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`
- 1448x1086 RGBA, x=0/y=0

Fixed drum:
- `character-assets/layers/drum/drum_base.png`
- SHA-256 `dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85`
- 1448x1086 RGBA, x=0/y=0

Do not move, mirror, regenerate, rescale, or overwrite these fixed layers during later-measure character work.

## Measures 5-8
- 33 notes / 32 groups, limb missing 0.
- Keys: BD:RF, RD:R, SN:L, BD+RC:*.
- Existing M1-4 frames cover BD, SN:L and BD+RC.
- Missing blocker: refreshed RD:R hit/rebound.
- Historical RD was rejected; current generation attempts were also rejected (wrong screen side / different character).
- Live runtime must not expand to M5-8 until a true baseline-derived RD pair passes composite QA.

## Measures 9-16
- 83 notes / 65 groups, limb missing 0.
- Additional keys: RD:R, BD+SN:RF/L, RC+SN:L/R.
- Refreshed BD+SN hit/rebound have passed static fixed-drum visual QA and are preserved:
  - `character-assets/layers/character/combo/bd_sn_hit_refresh.png`
  - `character-assets/layers/character/combo/bd_sn_rebound_refresh.png`
- Their manifest status is `VISUAL_QA_PASSED_RUNTIME_PENDING`; they are not runtime-mapped.
- RC+SN still requires regeneration; prior current-chat pair targeted the wrong crash side.
- RD remains the shared blocker from measures 5-8.

## Measures 17-148
FINAL chart after measure 16:
- 2,014 notes
- 1,403 time groups
- last measure 148
- embedded limb fields: 0

Analysis files:
- `site/charts/luna_say_maybe/Luna_say_maybe_full_limbs_DRAFT_ANALYSIS.json`
  - 1,819 mechanically resolved by existing rules
  - 195 unresolved
  - 179 rapid-SN notes
  - 8 simultaneous same-limb conflict groups
- `character-assets/prototypes/luna_say_maybe_16m/FULL_SONG_ACTION_KEY_INVENTORY_DRAFT.json`
  - part-combination counts only; no limb guessing

Neither draft is runtime authority. Formal rapid-SN rules and conflict resolution are required before a full-song limb sidecar can become authoritative.

## Canonical repository/site
- Repository: https://github.com/mleuatd/dtx-drum-flow
- Branch: main
- GitHub Pages: https://mleuatd.github.io/dtx-drum-flow/
