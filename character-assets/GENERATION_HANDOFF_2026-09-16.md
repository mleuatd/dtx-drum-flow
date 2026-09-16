# Character generation handoff — 2026-09-16

This file records the exact continuation point for the Luna Say Maybe full-song character animation work.

## Current main

- base commit inspected: `23da412e04105a4f01c90bd66428a77e80ffef6f`
- runtime scope: measures 1-148
- notes: 2,158
- simultaneous-time groups: 1,527
- unresolved runtime groups: 0
- groups still using fallback character poses: 575
- tom-only fallback groups: 100

## Existing registered character frames

- neutral
- HH right hit
- SN left hit
- SN left rebound
- BD right-foot down
- RC right hit
- RD right hit
- BD+SN hit
- BD+RC hit
- RC+SN hit

## Exact dedicated-image backlog

Single-part:
- `HT:R` -> `layers/character/ht/hit_r.png` + rebound
- `LT:R` -> `layers/character/lt/hit_r.png` + rebound
- `FT:R` -> `layers/character/ft/hit_r.png` + rebound
- HH left-hand prep/hit/rebound for R/L sixteenth alternation
- HH right rebound
- BD rebound
- RC rebound
- RD rebound

Combination keys currently using closest-pose fallback:
- `BD+LT:*`
- `RD+SN:*`
- `BD+RD:*`
- `BD+HH:*`
- `HH+SN:*`
- `FT+SN:*`
- `BD+HT:*`
- `LT+SN:*`
- `BD+HH+SN:*`
- `BD+RC+SN:*`
- `BD+FT+SN:*`
- `BD+FT:*`

## Asset rules that must remain locked

- canvas 1448x1086
- full-canvas transparent character layer; no trimming
- x=0, y=0
- fixed drum layer must never move or be regenerated
- left-facing/back-left character orientation
- rough monochrome hand-drawn line quality
- approved girl/outfit continuity must be preserved
- do not substitute a visually different girl, T-shirt/shorts design, or polished anime render

## Candidate review performed

Recent generated-image history was reviewed before writing this handoff.

Rejected for the authoritative runtime:
- a batch of ten clean line-art poses generated around 2026-09-16 08:25 UTC: wrong character/outfit (T-shirt/shorts), so not registered
- six HH/BD/BD+RC rebound candidates from around 05:08 UTC: pose direction is useful, but the source PNGs contain baked checkerboard/RGB backgrounds and therefore cannot be registered as transparent production layers without cleanup
- generated infographic/summary images: not runtime assets

Useful visual reference set:
- the earlier 01:52 UTC full-drum monochrome sketches retain the long-haired plaid-outfit drummer and the correct rear/left-facing composition. They are reference material only; they include the drum kit and therefore must not be registered directly as character-only layers.

## Next implementation order

1. HT/LT/FT dedicated hit + rebound layers
2. HH left-hand prep/hit/rebound
3. HH and BD rebounds
4. BD+HH, HH+SN, RD+SN
5. remaining tom/combo keys
6. update `assets_manifest.json`, `asset_inventory.json`, and `runtimePhaseFrameMap`
7. run asset validator + full-song fallback validator
8. require 1,527/1,527 resolved and reduce fallback count after each image batch
9. deploy and browser-QA the affected measures before continuing

Do not mark an item complete merely by remapping it to an existing wrong pose. Dedicated image work is complete only when the correct transparent layer is registered and the runtime phase map uses it.
