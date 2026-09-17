# Character Variant Status

## Authoritative state — 2026-09-17

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

Runtime scope is 28 notes / 27 groups. The temporary 1-16 runtime change was rolled back; `site/character-prototype.js` and `asset_inventory.json` are again aligned on measures 1-4.

Limb data remains authoritative:
- `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json`
- `site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json`

## Fixed drum
The current GitHub drum is still the older approved binary. A newer user-approved replacement is pending binary transfer.
Expected new SHA-256:
`afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`

Do not regenerate or reinterpret the drum. Do not change manifest drum hashes until the exact replacement binary is actually committed.

## Later-measure assets
Additional historical 1-16 character PNGs may still exist in the repository tree, but they are outside the active refreshed 1-4 visual scope and must not be treated as newly approved for expansion without explicit review.
