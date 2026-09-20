# Character Layer Rules

## Goal

Prevent positional jitter between animation frames by separating the completely fixed drum kit from character motion.

## Canonical canvas

- Width: 1448 px
- Height: 1086 px
- Origin: top-left
- Every layer must use the full canvas size.
- Do not trim transparent margins.
- Do not auto-crop.
- Do not resize individual frames.
- Composite offset is always x=0, y=0 unless an explicit migration is approved.

## Layer stack

Render bottom to top:

1. `drum` — immutable drum kit and hardware.
2. `character` — character body and performance pose.
3. `effect` — optional hit/rebound motion marks.
4. `debug` — optional development-only registration guides; never ship enabled.

The final visible frame is the alpha composite of these layers.

## Immutable drum layer

The drum layer includes every non-moving piece of hardware:

- hi-hat and stand
- crash / ride cymbals and stands
- snare
- rack toms
- floor tom
- bass drum
- pedals
- drum throne base when treated as fixed
- clamps / stands / feet / support hardware

Once `layers/drum/drum_base.png` is approved, its pixels and registration are locked.

## Character layer

The character layer may change only for performance motion:

- left/right arm
- wrist/hand
- stick
- foot/leg when a pedal is played
- slight upper-body follow-through
- slight hair follow-through

The character's global anchor does not move.

## Registration rules

Every PNG must:

- be exactly 1448x1086
- have transparent background except intended pixels
- use the same origin
- keep the baseline registration
- never be mirrored
- never be independently scaled or translated

Validation must fail when canvas size differs or when configuration requests non-zero offsets.

## Hand assignment

Normal default:

- quarter notes: one-hand pattern where physically natural
- eighth notes: one-hand pattern where physically natural
- sixteenth-note repeated hits: alternating hands by default

For HH sixteenth repeats, default sticking is:

`R L R L`

unless the chart explicitly overrides sticking.

## Git management

- Binary layers are stored under `character-assets/layers/`.
- Rules and score mappings are stored as JSON under `character-assets/config/`.
- Generated previews belong under `character-assets/previews/`.
- Generated previews are not authoritative; source layers + JSON rules are authoritative.
- Never regenerate an APPROVED layer unless the user requests revision.

## Score binding

A JSON chart note may optionally carry:

```json
{
  "time": 12.345,
  "part": "HH",
  "animation": {
    "rule": "hh.eighth.single",
    "hand": "R",
    "phase": "hit"
  }
}
```

If omitted, runtime selection uses `animation_rules.json` based on part, local subdivision, repetition, and simultaneous notes.


## Topology-preserving deformation

For a motion correction that crosses a joint chain or the waist/skirt boundary, do not use a rectangular pasted patch. Use one connected semantic region and a continuous deformation field.

Mandatory rules:

- Determine camera, torso direction, pelvis and stool contact before placing the active limb.
- For a pedal action, preserve the chain `hip -> knee -> ankle -> boot -> pedal` without reverse bends or detached segments.
- Transform body contour, clothing contour, checked fabric lines, skirt hem, boot details and alpha with the same deformation field.
- Masks follow the character silhouette and natural clothing/occlusion boundaries; bounding-box edges must never become visible seams.
- Fixed regions outside the declared deformation ROI must remain byte-identical whenever technically possible.
- The immutable drum layer is used for contact QA only and is never warped or baked into the character PNG.
- Save landmarks, source SHA, target contact, fixed ROI, deformation ROI and QA tolerances as versioned configuration data.
