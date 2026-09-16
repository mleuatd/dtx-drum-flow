# DTX Drum Flow — Shared Project Manifest

## Current highest-priority task — 2026-09-17
Complete the Luna Say Maybe **measures 1-4 only** character flipbook prototype.

Authoritative work handoff:
`character-assets/prototypes/luna_say_maybe_16m/WORK_HANDOFF_M1_4_2026-09-17.md`

Current image policy:
- fixed drum layer remains immutable
- character image rebuild starts from one approved neutral person+stool image
- all legacy character hit/rebound/combo/approved-pose PNGs were intentionally deleted
- do not recover/reuse deleted images
- create 10 new action variants from the neutral, resulting in 11 person frames total
- action keys: SN:L, SN:R, HH:R, BD:RF, BD+RC:*
- FINAL notes + limb JSON are authoritative for hands/feet
- prototype must not expand beyond measure 4 until separately approved

Important binary handoff note:
The newest user-approved neutral image from the originating chat must be attached/provided to Work and committed over `character-assets/layers/character/base/neutral.png` before variant generation. The GitHub neutral present before that replacement is not the visual-generation master.

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
Older full-song/1-16/1-8 milestones remain in Git history and CHANGELOG for reference, but they are not the active character-image scope.
