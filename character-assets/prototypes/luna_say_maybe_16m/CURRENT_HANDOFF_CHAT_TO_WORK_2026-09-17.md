# CURRENT HANDOFF — Chat / Work recovery point (2026-09-17)

This file is the current recovery point for the DTX Drum Flow Luna Say Maybe character task. Normal Chat and Work must both recover from GitHub `main` plus this file rather than relying on conversation memory.

## Repository / branch
- Repository: `mleuatd/dtx-drum-flow`
- Branch: `main`
- GitHub Pages: `https://mleuatd.github.io/dtx-drum-flow/`
- Always fetch latest `main` before changing anything.

## Active scope
The active visual-development unit is **Luna Say Maybe measures 1-4 first**.
Do not expand refreshed character-image work beyond measure 4 until this unit is visually accepted.
The existing 1-16 chart/limb metadata remains valid and must not be deleted.

## Runtime state — reconciled
The temporary commit `9950d7bd423e9e76766041404c5793758cc249c9` expanded runtime to measures 1-16 and caused an inventory mismatch.
That mismatch was corrected by commit:
`d8f621ec57ee00372aa9c987f0782b6e7a7065ea` (`prototype: restore Luna measures 1-4 runtime`).

Current runtime must remain:
- `site/character-prototype.js`: measures 1-4
- `asset_inventory.json`: measures 1-4
- notes: 28
- groups: 27
- unresolved limbs: 0
- action keys: `SN:L`, `SN:R`, `HH:R`, `BD:RF`, `BD+RC:*`

Opening limb sequence:
- 4.714583 SN:L
- 4.930410 SN:R
- 5.038324 SN:L
- 5.146237 BD:RF + RC:R

## Current character frame set
GitHub `main` currently contains the neutral plus the 10 first-four-measure hit/rebound variants referenced by the current inventory and manifest. Do not describe the repository as a two-image-only baseline unless those files are actually removed.

Required 1-4 frame set:
1. neutral
2. SN:L hit
3. SN:L rebound
4. SN:R hit
5. SN:R rebound
6. HH:R hit
7. HH:R rebound
8. BD:RF hit
9. BD:RF rebound
10. BD+RC hit
11. BD+RC rebound

Character PNGs are person+stool only. Fixed drum is separate. Registration remains 1448x1086 at x=0,y=0.

## Fixed drum replacement — pending binary task
The user approved a new fixed drum PNG in the originating chat.

Exact required replacement:
- target: `character-assets/layers/drum/drum_base.png`
- PNG
- 1448x1086
- RGBA with real transparency
- drums only; no person, stool, UI, or background
- source file SHA-256: `afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`
- local originating-chat file: `/mnt/data/5200.png`

Current GitHub drum is still the older binary:
- Git blob SHA: `30a18a87ca3c1dc6db2d9fabe73be1ff48011370`
- GitHub blob size: 352715 bytes
- manifest SHA-256 lock: `6a439481eb829a83bad1e7ccfd4cfb0fe352663adeeda6fdba4a91337799d50d`

Do not regenerate, redraw, resize, recompress, recolor, or alter alpha. The new source PNG must be transferred byte-for-byte.

Commit message for the binary replacement:
`assets: finalize corrected 11-lane drum layer`

## Drum manifest follow-up
Only after the new binary is confirmed in GitHub, update all old drum SHA references, including at minimum:
- `character-assets/config/assets_manifest.json`
- `character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json`
- QA/status files still pinning the old drum hash

Then use a separate commit such as:
`chore: lock finalized 11-lane drum asset`

Do NOT change the manifest first while GitHub still contains the old binary.

## Rules that must not be lost
- GitHub `main` is the code/data source of truth.
- This file records the current user intent and pending binary handoff.
- Do not regenerate the fixed drum.
- Do not mirror or change the approved character camera direction.
- Do not mix drum hardware into character PNGs.
- Do not treat historical 1-16 image experiments as newly approved refreshed assets.
- Commit/push after each meaningful milestone so usage limits do not erase progress.

## Current state checklist
- runtime restored to 1-4: YES
- inventory aligned to 1-4: YES
- 1-4 action frame files present: YES
- new approved drum binary committed: NO
- manifest updated to new drum SHA: NO
- next binary target SHA-256: `afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`

The next agent/chat must continue from this state without asking the user to reconstruct earlier history.
