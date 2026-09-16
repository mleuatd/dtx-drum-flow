# Luna Say Maybe — 16-measure character animation prototype

This is the first implementation target for DTX Drum Flow's drummer-character animation.

## Scope

- Song: Luna Say Maybe
- Measures: 1 through 16 only
- Source chart: `site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json`
- Default drummer: right-handed
- Default kit technique: cross-hand
- HH: right hand for ordinary quarter/eighth patterns
- HH repeated sixteenths: alternate R/L
- SN: left hand by default
- BD: right foot
- HH pedal / LP: left foot
- Cymbals: right hand by default
- Tom runs: alternate R/L, beginning with R unless a later reviewed sticking map overrides it
- Simultaneous hits are grouped inside an 8 ms window

## Goal

Use these 16 measures as the prototype before expanding to the whole song.

The prototype must prove:

1. drum layer remains completely fixed
2. character-only pose layers can change without drum jitter
3. each note resolves to an animation rule
4. right/left hand selection is stable across repeated notes
5. simultaneous notes resolve to a combined pose when needed
6. the browser can switch the visible character pose in time with chart notes

## Generated prototype data

`Luna_say_maybe_16m_animation.json` contains the first 16 measures with per-note `animation` metadata.

This file is generated from the FINAL chart and is the authoritative prototype mapping until manual sticking review changes a note.

## Baseline orientation

The approved character orientation is LEFT-facing from the fixed rear three-quarter camera. Do not generate right-facing replacements. Do not mirror the baseline.

## Asset rule

The approved image is split conceptually into:
- fixed drum layer
- character pose layer

Both use the same 1448x1086 canvas and x=0,y=0 registration.

Binary layer PNGs are only authoritative after they are committed under:
- `character-assets/layers/drum/drum_base.png`
- `character-assets/layers/character/base/neutral.png`

Future pose PNGs inherit this registration.
