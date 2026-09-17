# CURRENT HANDOFF — Normal Chat -> Work (2026-09-17)

This file is the current recovery point for the DTX Drum Flow Luna Say Maybe character task.

## Repository / branch
- Repository: `mleuatd/dtx-drum-flow`
- Branch: `main`
- GitHub Pages: `https://mleuatd.github.io/dtx-drum-flow/`
- Always fetch latest `main` before changing anything.

## User intent that must be preserved
The active visual-development unit is **Luna Say Maybe measures 1-4 first**. Complete and visually verify this unit before expanding refreshed character-image work beyond measure 4.

Do not discard the existing 1-16 chart/limb metadata. `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json` remains authoritative for limb assignments.

## Important current inconsistency
Normal Chat created commit `9950d7bd423e9e76766041404c5793758cc249c9` (`prototype: restore Luna measures 1-16 runtime`). This changed `site/character-prototype.js` to `PROTOTYPE_MEASURE_END=16` while the current `asset_inventory.json`, project manifest, WORK_SYNC override, and visual task are still measures 1-4.

Treat this as an **incomplete/inconsistent intermediate state**, not as approval to skip the 1-4 prototype process. Before further feature expansion, reconcile runtime scope and inventory deliberately. Do not silently assume either file is fully authoritative by itself.

## Fixed drum replacement — pending and highest priority binary task
The user approved a new fixed drum PNG from the originating chat.

Expected source binary properties:
- PNG
- 1448x1086
- RGBA with real transparency
- drums only; no person, stool, UI, background
- target path: `character-assets/layers/drum/drum_base.png`
- expected SHA-256: `afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`

The approved new drum binary was **NOT committed by Normal Chat as of this handoff**. Current GitHub `drum_base.png` is still the older binary referenced by the old manifest SHA.

When the approved PNG is available in Work, replace the target file byte-for-byte without regeneration, redraw, resize, recompression, color conversion, or alpha modification. Prefer ordinary local `git add/commit/push` in Work. Commit the image separately with:

`assets: finalize corrected 11-lane drum layer`

Then verify GitHub copy SHA-256 equals the expected SHA above.

## Drum manifest follow-up
Only after the new binary is confirmed in GitHub, update all drum SHA locks/references, including at minimum:
- `character-assets/config/assets_manifest.json`
- `character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json`
- any QA/status file still pinning the old drum SHA

Use a separate commit, e.g.:
`chore: lock finalized 11-lane drum asset`

Do NOT update manifests first while the old binary is still present.

## Measures 1-4 character task
The current intended 1-4 action keys are:
- `SN:L`
- `SN:R`
- `HH:R`
- `BD:RF`
- `BD+RC:*`

Expected first-4 scope:
- 28 notes
- 27 time groups
- unresolved limbs: 0

Opening limb sequence must remain:
- 4.714583 SN:L
- 4.930410 SN:R
- 5.038324 SN:L
- 5.146237 BD:RF + RC:R

Person-frame plan for the refreshed 1-4 flipbook is neutral + hit/rebound variants for those keys. Character PNGs are person+stool only; fixed drum remains a separate immutable layer. Preserve 1448x1086, x=0,y=0 registration.

## Do not lose these rules
- GitHub latest main is the code/data source of truth, but this handoff records the current user intent and resolves stale historical text.
- Do not regenerate the fixed drum.
- Do not change the approved camera direction / mirror the person.
- Do not mix drum hardware into character PNGs.
- Do not treat old historical 1-16 image experiments as newly approved visual assets.
- Commit incrementally so Work usage limits do not erase progress.
- After each meaningful binary/image milestone, push before generating the next batch.

## Recommended recovery sequence for Work
1. Fetch latest `main` and record HEAD.
2. Read this file, `WORK_SYNC.md`, `PROJECT_MANIFEST.md`, `VARIANT_STATUS.md`, `LAYER_RULES.md`, `assets_manifest.json`, `asset_inventory.json`, and the existing 1-4 handoff/spec.
3. Confirm current runtime/inventory mismatch caused by commit `9950d7bd...`.
4. Commit the approved new drum binary first if it is attached/available.
5. Update drum SHA locks only after binary verification.
6. Reconcile the prototype back to a coherent measures 1-4 visual-development state unless the user explicitly changes scope.
7. Run repository/character/chart/UI/build QA and push.
8. Continue refreshed 1-4 character flipbook work, committing/pushing incrementally.
9. Only after 1-4 is visually accepted, proceed to later measures.

## Normal Chat known state at handoff creation
- Latest main before creating this handoff: `9950d7bd423e9e76766041404c5793758cc249c9`
- 1-16 runtime commit exists: yes, intermediate/inconsistent
- New approved drum binary committed: no
- Manifest updated to new drum SHA: no
- `asset_inventory.json` still describes measures 1-4: yes
- Work should not ask the user to reconstruct these facts again; recover from GitHub + this file and continue.
