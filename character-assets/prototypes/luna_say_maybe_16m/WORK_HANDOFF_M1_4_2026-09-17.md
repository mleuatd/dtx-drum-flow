# WORK HANDOFF — Luna Say Maybe measures 1-4 character flipbook
Date: 2026-09-17

## Mission
Complete the Luna Say Maybe **measures 1-4 only** character flipbook prototype from the current GitHub `main`, including image creation, registration, implementation, QA, commit/push, and GitHub Pages deployment.

Do not ask the user for routine confirmation. Work autonomously and commit incrementally.

## Canonical starting point
Repository: `mleuatd/dtx-drum-flow`
Branch: `main`
Public URL: https://mleuatd.github.io/dtx-drum-flow/

GitHub `main` is the source of truth for code, chart/limb data, drum layer, manifests, and runtime rules.

### Critical image exception
The user has just approved a **new latest neutral image** in the originating ChatGPT conversation. It is a person+stool-only rough monochrome drawing and is visually approved as the new neutral origin.

At the time this handoff file was written, that newest binary neutral had **not yet been uploaded to GitHub**. Therefore:
- when starting this Work task, the user should attach/provide that latest approved neutral image together with this instruction;
- replace `character-assets/layers/character/base/neutral.png` with that attached image before generating variants;
- do NOT use the older GitHub neutral as a visual-generation reference if the attached latest neutral is available;
- once the latest neutral is committed, GitHub becomes the source of truth again.

If the latest neutral image is not attached/available, stop image generation rather than inventing another neutral.

## Current image-management state
GitHub was intentionally reset to remove reference noise.

Only these two authoritative layer PNG paths remain:
1. `character-assets/layers/drum/drum_base.png`
2. `character-assets/layers/character/base/neutral.png`

All old hit/rebound/combo/prototype-approved pose PNGs were deleted intentionally. Do not recover or reuse them.

The drum image is immutable. Verify SHA before and after work:
`eba6161535535d935e518cdcc9009ad75ee9a3f5e57cd66ba2128deaed044b30`

## Read these files first
- `WORK_SYNC.md`
- `PROJECT_MANIFEST.md`
- `CHANGELOG.md`
- `character-assets/VARIANT_STATUS.md`
- `character-assets/LAYER_RULES.md`
- `character-assets/BASELINE_LOCK_2026-09-16.md`
- `character-assets/config/assets_manifest.json`
- `character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json`
- `character-assets/prototypes/luna_say_maybe_16m/PARAPARA_CHARACTER_SPEC_2026-09-17.md`
- `character-assets/prototypes/luna_say_maybe_16m/CHARACTER_IMAGE_GUIDE_2026-09-17.md`
- `character-assets/prototypes/luna_say_maybe_16m/NEUTRAL_STYLE_LOCK_2026-09-17.md`
- `site/character-prototype.js`
- `site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json`
- `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json`

## Scope
Only measures **1-4**.

Recompute the real note/action coverage from FINAL notes + limb JSON before wiring images.

Expected action keys for measures 1-4:
- `SN:L`
- `SN:R`
- `HH:R`
- `BD:RF`
- `BD+RC:*`

Important known opening:
- 4.714583 SN:L
- 4.930410 SN:R
- 5.038324 SN:L
- 5.146237 BD:RF + RC:R

SN is not always left hand. Limb JSON is authoritative.

Expected scope:
- 28 notes
- 27 time groups
- unresolved = 0

## Required final person-frame set
Total person+stool PNGs for measures 1-4: **11**.

1. neutral
2. SN:L_hit
3. SN:L_rebound
4. SN:R_hit
5. SN:R_rebound
6. HH:R_hit
7. HH:R_rebound
8. BD:RF_hit
9. BD:RF_rebound
10. BD+RC_hit
11. BD+RC_rebound

Drum layer is separate and not included in these 11.

## Image-generation rule: edit the neutral, do not redraw the character
The approved latest neutral is the absolute origin.

Every hit/rebound frame must look like the **same drawing with only the necessary limbs moved**.

Keep fixed:
- face position
- head size
- torso
- waist/hips
- thighs
- boots
- stool/chair
- overall hair volume and silhouette
- character scale
- canvas registration
- body/camera direction

May move only as needed:
- upper arm
- forearm
- wrist
- drumstick angle
- right-foot pedal motion
- tiny shoulder tilt
- tiny torso lean

Do not:
- redraw the whole person
- change face/head/body proportions
- change hair design
- remove/change the stool
- mirror the pose
- alter camera direction
- introduce the drum into character PNGs

## Neutral visual lock
Style:
- monochrome rough line art
- many scribbly/overlapping strokes
- hand-drawn, intentionally imperfect
- rough construction/hesitation lines may remain
- not polished clean digital line art
- no color fill
- no gradient
- 4-head-ish chibi proportion
- long hair
- plaid long jacket
- dark pleated skirt
- socks
- chunky lace-up boots

Neutral pose:
- ordinary pre-hit ready position
- both hands naturally holding drumsticks
- no instrument is being struck
- no dramatic action

## Camera/body direction
Keep exactly the approved neutral's direction.
Do not mirror.
Do not switch to front / exact side / exact rear.

## Layer rules
Character PNG contains:
- person
- stool/chair

Character PNG excludes:
- drum kit
- cymbals
- drum hardware
- background
- lane
- notes
- UI
- effect

Fixed drum:
`character-assets/layers/drum/drum_base.png`

All character PNGs:
- 1448x1086
- transparent background
- x=0, y=0
- same scale
- same position

## Motion states
`neutral -> hit -> rebound -> neutral`

Timing:
- 0-90ms: hit
- 90-170ms: rebound
- >=170ms: neutral unless next note is closer

Next-note rules:
- gap <90ms: hit -> next hit
- gap 90-170ms: hit -> rebound -> next hit
- gap >=170ms: hit -> rebound -> neutral

Do not interpolate smoothly. Preserve a slightly choppy hand-drawn flipbook feel.

## Per-action requirements
### SN:L
Hit: left hand strikes snare; change mostly left arm/wrist/stick.
Rebound: intermediate between hit and neutral.

### SN:R
Hit: right hand strikes snare; change mostly right arm/wrist/stick.
Rebound: intermediate between hit and neutral.

### HH:R
Hit: right hand reaches HH.
Rebound: right arm partially returns.

### BD:RF
Hit: right foot presses BD.
Rebound: right foot partially releases.
Upper body should barely change.

### BD+RC
Hit: right foot BD + right hand RC simultaneously.
Rebound: right arm/right foot partially return.
Head/waist/stool remain fixed.

## Runtime implementation
Use:
- FINAL notes
- limb JSON
- `runtimeFrameMap`
- `runtimePhaseFrameMap`

Do not reference frameMap before inventory is initialized.
For combo validation resolve keys against `inventory.runtimeFrameMap`.

Prototype hard scope must remain measures 1-4.

## Layer order
1. drum
2. character
3. effect
4. notes Canvas
5. controls

Luna Canvas remains transparent.

## HUD
Keep development HUD visible until final QA is complete:
- BUILD
- JS
- CHAR
- active
- state
- frame
- phase
- key
- err

## Cache busting
Use one new version string across:
- index.html -> app.js
- app.js -> character-prototype.js
- character-prototype.js -> PNG URLs
- styles.css

Suggested format:
`20260917-m1-4-parapara-rN`

## Git strategy
Commit/push incrementally. Suggested commits:
1. `assets: lock approved Luna neutral baseline`
2. `assets: add Luna measures 1-4 hit and rebound variants`
3. `feat: implement Luna measures 1-4 parapara animation`
4. `fix: stabilize Luna flipbook transitions`
5. `test: verify Luna measures 1-4 parapara runtime`

Binary PNGs must be committed to GitHub, not left only in Work/container storage.

## Required QA
Image QA:
- all PNG readable
- 1448x1086
- real alpha
- stool present
- no drum mixed into character frames
- registration/scale stable
- neutral visual identity preserved

Chart/limb QA:
- reparse measures 1-4
- limb missing = 0
- unresolved = 0
- exactly the five expected keys resolve
- BD+RC:* resolves correctly

Animation QA:
- neutral -> hit -> rebound -> neutral
- rapid notes do not reset to neutral unnecessarily
- idle gap returns neutral
- intentionally choppy, not overly smooth
- no body/stool jump between frames

UI QA:
- character visible behind notes
- Luna canvas transparent
- Android/Xperia viewport
- HUD visible during development
- cache versions aligned

CI / validation:
- node --check
- chart validation
- UI contract
- character asset validation
- standalone build
- deploy-site

## Finalization
After successful QA:
- update manifests/inventory SHA values
- update `VARIANT_STATUS.md`
- update `CHANGELOG.md`
- update this handoff or create a completion handoff
- verify GitHub Pages deployment
- provide cache-busted public URL

Do not extend to measure 5+ in this Work task.
