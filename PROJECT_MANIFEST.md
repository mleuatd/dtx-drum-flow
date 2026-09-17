# DTX Drum Flow — Shared Project Manifest

## Current highest-priority task — 2026-09-17
Complete and verify the Luna Say Maybe **measures 1-4** character flipbook prototype before expanding refreshed visual work beyond measure 4.

Current authoritative recovery file:
`character-assets/prototypes/luna_say_maybe_16m/CURRENT_HANDOFF_CHAT_TO_WORK_2026-09-17.md`

## Current coherent runtime state
- Runtime scope: measures 1-4
- `site/character-prototype.js`: `PROTOTYPE_MEASURE_END=4`
- `asset_inventory.json`: measures 1-4 / 28 notes / 27 groups
- Action keys: `SN:L`, `SN:R`, `HH:R`, `BD:RF`, `BD+RC:*`
- 1-16 limb metadata remains authoritative and must not be deleted.
- The accidental temporary 1-16 runtime expansion in commit `9950d7bd...` was corrected by commit `d8f621ec57ee00372aa9c987f0782b6e7a7065ea`.

## Character image state
The GitHub tree currently contains the neutral person+stool baseline and the 10 measures 1-4 hit/rebound variants referenced by `assets_manifest.json` and `asset_inventory.json`.
Do not describe the repository as a two-image-only baseline unless those files are actually removed again.

## Fixed drum state
Current GitHub `character-assets/layers/drum/drum_base.png` is still the older binary (Git blob `30a18a87ca3c1dc6db2d9fabe73be1ff48011370`, size 352715 bytes).
The user-approved replacement exists in the originating chat as an exact 1448x1086 RGBA PNG with SHA-256:
`afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`
It must replace `drum_base.png` byte-for-byte; do not regenerate, redraw, resize, recompress, recolor, or alter alpha.
Do not update drum SHA locks before the binary replacement itself is confirmed in GitHub.

## Canonical site
- GitHub repository: https://github.com/mleuatd/dtx-drum-flow
- Default branch: main
- GitHub Pages: https://mleuatd.github.io/dtx-drum-flow/

## Fixed registration
- canvas: 1448x1086
- registration: x=0,y=0
- fixed drum + separate character + optional effects
- never move/regenerate the drum per character frame
- validation: `tools/character_layers/validate_assets.py`

## Historical context
Older full-song/1-16/1-8 milestones remain in Git history and historical QA files, but they are not the active refreshed visual scope.
