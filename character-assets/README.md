# DTX Drum Flow — Background Character Assets

This directory is the canonical management location for drummer background-character layers and animation variants used by DTX Drum Flow.

## AI / new-chat entrypoint

Before any character-image PLAN / EDIT / RETRY / VISUAL_QA / APPROVE work, start with:

- `AI_IMAGE_WORK_ENTRYPOINT.md`

That entrypoint requires the latest-main versions of:
- `AI_OPERATION_MASTER_RULES.md`
- `IMAGE_DECISION_POLICY.md`
- `CURRENT_WORK_ORDER.json`
- `IMAGE_WORK_PREFLIGHT.json`
- `CHARACTER_FAILURE_KNOWLEDGE.json`
- `CHARACTER_ASSET_PIPELINE.md`
- `LAYER_RULES.md`

Do not select an image-editing technique first. Resolve the active motion and completed donors first, then choose the least destructive method.

## Fixed baseline rules

The approved rough black-and-white drummer composition is the baseline/origin for all future variants.

Keep fixed across every variant:
- camera angle
- rear-side elevated three-quarter view
- composition and distance
- character facing direction
- drum-kit layout
- drum/stool registration
- visibility of the whole kit
- about 4-head chibi proportion
- monochrome rough line-art style
- dense, messy, hand-drawn searching lines
- amateur/sketch-like unevenness
- white background / black lines

Only performance motion may change:
- stick position
- arm position
- foot/leg when a pedal is played
- subtle upper-body motion
- slight hair follow-through
- struck instrument
- hit / rebound phase

## Layer architecture

The authoritative image is no longer a monolithic frame.

A visible frame is composed from independent full-canvas layers:

1. `layers/drum/drum_base.png` — immutable drum kit.
2. `layers/character/<part>/<pose>.png` — character motion only.
3. `layers/effect/<effect>.png` — optional impact/motion marks.

Every layer is 1448x1086 and registered at x=0,y=0.

Do not:
- crop
- translate
- scale
- mirror
- re-render the drum kit inside every pose

See `LAYER_RULES.md`.

## Animation / score mapping

Authoritative mappings live in:

- `config/layer_manifest.json`
- `config/animation_rules.json`
- `config/chart_bindings.json`
- `config/lane_map.json`

Charts may optionally embed an `animation` object per note. If omitted, animation is selected automatically from part + note spacing + simultaneous-hit grouping.

See `SCORE_BINDING.md`.

## Hand rules

Default behavior:
- quarter-note repeated HH: one hand
- eighth-note repeated HH: one hand
- sixteenth-note repeated HH: alternating hands
- default HH sixteenth sticking: R L R L

The same alternating strategy is available for fast SN/tom repeats.

## Tooling

Validate registration:

```bash
pip install -r tools/character_layers/requirements.txt
python tools/character_layers/validate_assets.py
```

Composite one frame:

```bash
python tools/character_layers/compose_layers.py hh/hit_r output.png
```

GitHub Actions runs the registration validator automatically when character assets change.

## Naming

Use lowercase ASCII filenames.

Examples:

- `layers/character/hh/prep_r.png`
- `layers/character/hh/hit_r.png`
- `layers/character/hh/rebound_r.png`
- `layers/character/hh/hit_l.png`
- `layers/character/sn/hit_r.png`
- `layers/character/bd/foot_down.png`
- `layers/character/combo/sn_bd_hit.png`

## Progress source of truth

See `VARIANT_STATUS.md`.

Generated GIFs/previews are review artifacts only. The source of truth is always the fixed drum layer + character layer(s) + JSON rules.
