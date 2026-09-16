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

## Current runtime milestone

The browser now enables measures 1 through 16 as the reviewed prototype runtime milestone.
Measures 9 through 16 reuse the already committed BD+SN and RC+SN simultaneous-hit
character layers, so no additional PNG generation is required for this 16-measure prototype.

Measures 1-4 contain 28 notes in 27 time groups and use only:
- SN left-hand hit
- BD right-foot hit
- HH right-hand hit
- BD + RC simultaneous hit

Each group is rendered as a short flipbook cycle: prep before the chart time, hit at
the chart time, then rebound. SN has a dedicated left-hand rebound drawing. The
other first-four-measure keys safely return to neutral until transparent dedicated
rebound drawings pass validation. A separate SVG effect layer emits short comic
bursts at the struck instrument coordinates; simultaneous BD + RC emits two bursts.

Measures 5-8 add 33 notes in 32 time groups and use:
- RD right-hand hit
- SN left-hand hit
- BD right-foot hit
- BD + RC simultaneous hit

Measures 9-16 complete the prototype window and add:
- BD + SN simultaneous hit
- RC + SN simultaneous hit
- existing HH / SN / BD / RD / BD+RC poses where applicable

The full measures 1-16 runtime contains 144 notes in 124 time groups.

For non-rapid notes, hit follow-through ends after 0.075 seconds and the character
returns to the approved neutral stance. Repeated hits separated by 0.13 seconds or
less are treated as sixteenth-speed continuity and keep the rebound pose instead of
resetting between hits.

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

`site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json` contains the reviewed first-16-measure per-note limb assignments and is authoritative for runtime sticking in this scope. The renderer consumes these precomputed values before any legacy part-default fallback.

The phrase-aware exception is the short SN pickup at 4.930410s -> 5.038324s. It is assigned R -> L so the immediately following 5.146237s crash can remain on the right hand. Measures 1-16 contain no HT/LT/FT notes.

## Approved exact poses restored

- Measure 1, 4.930410s, SN:R now uses the user-approved `approved/pose_01.png`, registered at `layers/character/sn/hit_r.png`.
- BD+RC uses the user-approved `approved/pose_03.png`, registered at `layers/character/combo/bd_rc_hit.png`.
- Both remain on the locked 1448x1086 registration with real transparency.

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
## Prototype boundary

This prototype is intentionally limited to measures 1-16. Measure 17+ remains out of scope until the 1-16 result is visually accepted.

## 2026-09-17 final 1-16 pass

Runtime scope is explicitly measures 1-16 (144 notes / 124 groups). The authoritative limb source remains `Luna_say_maybe_1_16_limbs.json`. The previously missing SN:R exact pose at 4.930410s has been restored from the user-approved pose_01; it no longer falls back to neutral. Structural PNG QA is recorded in `FINAL_QA_2026-09-17.md`. No measure 17+ image generation is part of this prototype pass.
