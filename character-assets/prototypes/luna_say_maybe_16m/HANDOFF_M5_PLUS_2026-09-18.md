# HANDOFF — Luna Say Maybe refreshed measures 5+ expansion
Date: 2026-09-18

## Mission
Continue from the completed refreshed M1-4 character flipbook without changing its character identity, camera, registration, fixed drum, or approved runtime behavior.

Repository: `mleuatd/dtx-drum-flow`
Branch: `main`
Public URL: https://mleuatd.github.io/dtx-drum-flow/

## Completed before this handoff
Measures 1-4 remain the live refreshed runtime and are fully live-browser QA'd.

Approved fixed neutral SHA-256:
`886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`

Approved fixed drum SHA-256:
`dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85`

Do not replace or modify either fixed baseline while creating later-measure character variants.

## Work completed in this M5+ session

### Measures 5-8 analyzed
- authoritative source: FINAL notes + `Luna_say_maybe_1_16_limbs.json`
- 33 notes / 32 time groups
- keys: BD:RF, RD:R, SN:L, BD+RC
- approved reuse: BD, SN:L, BD+RC
- required new refreshed frames: RD:R hit + rebound

Historical `character-assets/layers/character/rd/hit_r.png` was not trusted. It was composited over the current fixed drum together with the M1-4 baseline through GitHub Actions.
- Visual QA run: `35315598184`
- artifact: `10535695236`
- result: REJECTED
- reason: different line treatment, proportions, hair/head/body rendering, seated registration and camera/body presentation.

Definition:
`M5_8_REQUIRED_CHARACTER_ASSETS.json`

QA issue:
`CHAR-QA-0005`

### Measures 9-16 analyzed
- 83 notes / 65 groups
- missing limb assignments: 0
- group key counts:
  - BD:RF = 13
  - RD:R = 4
  - SN:L = 3
  - BD+RC RF/R = 3
  - HH:R = 27
  - BD+SN RF/L = 14
  - RC+SN L/R = 1

Historical BD+SN and RC+SN hit PNGs were also composited and inspected.
- Visual QA run: `35315877548`
- artifact: `10535690785`
- result: REJECTED
- reason: same older/different drawing family; substantially narrower/shifted alpha bounds and visibly different line/character rendering.

Definition:
`M9_16_REQUIRED_CHARACTER_ASSETS.json`

QA issue:
`CHAR-QA-0006`

### Refreshed images required before M5-16 can be wired
Six new PNGs total, all direct edits of the current approved M1-4 character:
1. RD:R hit
2. RD:R rebound
3. BD+SN RF/L hit
4. BD+SN RF/L rebound
5. RC+SN L/R hit
6. RC+SN L/R rebound

Do not use the historical RD / BD+SN / RC+SN images.

### Measures 17-148 limb gap
FINAL chart:
- total notes: 2,158
- notes after measure 16: 2,014
- final measure: 148
- embedded limb/hand/foot fields after measure 16: 0

Repository search found only:
- `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json`
- `character-assets/prototypes/luna_say_maybe_16m/hand_rules.json`
- `LIMB_QA_2026-09-16.md`

The per-note authoritative limb assignment ends at measure 16. `hand_rules.json` is a prototype rule specification, not a precomputed full-song sidecar. Per user rule, do not invent hands/feet for measure 17+.

## Current blocker
The exact approved neutral was successfully recovered from GitHub visual-QA artifacts and can be inspected pixel-for-pixel in this normal chat. However, the available image-editing interface cannot accept that repository/artifact binary as a direct edit target in the same workflow. Project rules explicitly prohibit generating a look-alike person from scratch.

Therefore image generation was intentionally stopped rather than degrading the established M1-4 consistency. No rejected historical later-measure image was wired into runtime.

## Next exact actions
1. Make the exact approved neutral/M1-4 PNG available to the image editor as an actual editable image target.
2. Create RD:R hit/rebound first by moving only the right arm/wrist/stick and minimal shoulder/torso movement.
3. Run composite QA over fixed drum; update CHAR-QA-0005.
4. Register the approved RD frames, update manifests/inventory, extend refreshed runtime to measures 1-8, run live PC/Xperia runtime QA, commit/push/deploy.
5. Create BD+SN and RC+SN hit/rebound the same way; QA; extend to measures 1-16; live QA.
6. Before measure 17+, create and validate an authoritative full-song per-note limb sidecar from established project rules; do not use ad-hoc renderer inference.
7. Continue later-measure action-key inventory and image creation block by block.

## Commits from this session
- `d62c2c6c6422a6cb64fdc18d253dc56ff2f0d3c8` — add RD candidate to visual QA
- `485781572cd2cfe465047fd40285a1cb3ebadc02` — reject historical RD pose in QA ledger
- `b9cfadeeeb158d53a6eb7059dac9b47d64c88c2f` — define M5-8 required assets
- `99a6099125668e7e8abb5f40014e02e5e37fe258` — add M9-16 combo candidates to visual QA
- `6e42c64a42e0536a27018558a8ff45284ca78dc6` — reject historical M9-16 combo poses
- `0ca9da9ff47b7484410ef4323ea76a486c14aa5d` — define M9-16 required assets
- `e63abf068f032d45386b025a5fd143c7a44006a0` — update variant expansion status
- `6f863cfed4cbb68fb39e4ae9219cb1abbf549d0c` — update project current task/state
- `9a7632f65d31edfcd56ff23edc91f473e16178a6` — changelog

The commit creating this handoff becomes the final session commit unless further work follows.
