# Character Variant Status

## Authoritative state — 2026-09-17

The Luna Say Maybe prototype is now reset to a clean two-image baseline.

Authoritative images:
1. `character-assets/layers/drum/drum_base.png` — fixed drum layer
2. `character-assets/layers/character/base/neutral.png` — person + stool neutral baseline

All previous hit / rebound / combo / approved-pose PNGs were intentionally deleted from `main` so they cannot be reused as generation references by later chats.

Prototype scope: **measures 1-4**.

Limb data remains authoritative:
- `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json`
- `site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json`

1-4 action keys:
- `SN:L`
- `SN:R`
- `HH:R`
- `BD:RF`
- `BD+RC:*`

Until new variants are created, every action key intentionally resolves to neutral. New hit/rebound images must be derived only from the locked neutral; deleted legacy poses must not be used as references.
