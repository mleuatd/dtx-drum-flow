# Character Variant Status

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

## Fixed drum
The fixed drum was replaced on 2026-09-18 from the user-approved canonical source `/mnt/data/5215.png` after exact SHA-256 verification.

Canonical source SHA-256:
`6d23c74667f453162bcb508cec56bfe82a5a9804eba210a3c0e6a4670dd03c30`

Runtime transparent drum SHA-256:
`ad09946851e4184e466fb065c7491926a8bd8043bfd48f100b188af1c646f8a6`

Runtime path:
`layers/drum/drum_base.png`

The approved drawing was not regenerated or reinterpreted; the white background was converted to alpha for runtime use. Pedal interpretation is fixed as: left = hi-hat pedal, center = bass drum pedal, and this is not a twin-pedal setup.

## Later-measure assets
Additional historical 1-16 character PNGs may still exist in the repository tree, but they are outside the active refreshed 1-4 visual scope and must not be treated as newly approved for expansion without explicit review.
