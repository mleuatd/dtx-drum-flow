# DTX Drum Flow — Background Character Assets

This directory is the canonical management location for the drummer background-character image variants used by DTX Drum Flow.

## Fixed baseline rules

The current attached rough black-and-white drummer image is the **baseline/origin image** for all future variants.

Keep fixed across every variant:
- camera angle
- rear-side elevated three-quarter view
- composition and distance
- character facing direction
- overall drum-kit layout
- visibility of the whole kit
- about 4-head chibi proportion
- monochrome rough line-art style
- dense, messy, hand-drawn searching lines
- amateur/sketch-like unevenness
- white background / black lines

Only performance motion may change:
- stick position
- arm position
- foot position
- subtle body motion
- struck instrument
- hit / rebound phase

## Naming

Use lowercase ASCII filenames so the site can reference assets safely.

`baseline/default.png`

Single-part variants:
`variants/<part>/<phase>-<rate>.png`

Examples:
- `variants/sn/hit-quarter.png`
- `variants/sn/rebound-quarter.png`
- `variants/hh/hit-eighth.png`
- `variants/bd/hit-sixteenth.png`

Simultaneous-hit variants:
`variants/combo/<parts>-<phase>-<rate>.png`

Examples:
- `variants/combo/sn-bd-hit-quarter.png`
- `variants/combo/hh-bd-hit-eighth.png`

## Progress source of truth

See `VARIANT_STATUS.md`.
