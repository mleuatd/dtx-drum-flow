# Donor / Mesh Repair Specification v1

This directory is the mandatory policy layer for character repair.

Resolution order:
`GLOBAL_COMMON -> INSTRUMENT_TEMPLATE -> LIMB_PHASE_TEMPLATE -> ACTION_COMBINATION_TEMPLATE -> FRAME_OVERRIDE`.

The fixed drum and instrument contact coordinates are external authorities and must not be re-invented here:
- `character-assets/prototypes/luna_say_maybe_16m/INSTRUMENT_CONTACT_POINTS.json`
- `character-assets/prototypes/luna_say_maybe_16m/POSE_TRANSITION_RULES.json`
- `character-assets/prototypes/luna_say_maybe_16m/FAILURE_PATTERN_REGISTRY.json`

Repair method precedence is safety-first:
1. direct same-action replacement
2. local artifact removal
3. same-instrument donor
4. cross-instrument donor + local mesh retarget
5. composite-only validation
6. HOLD

The parent is `PRE15_BASELINE_MERGED_WITH_AI_PASS`; current `main` character PNGs are never an automatic parent.

Machine PASS never replaces full-resolution visual QA.
