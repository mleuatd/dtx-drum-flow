# Generated Character Edit Instruction — RC+SN:R/L hit

Action key: `RC+SN:R/L`
Phase: `hit`
Queue: `ASSETQ-001`
Block: `B09_16`

Use the exact approved neutral character layer as the edit source and registration baseline.

Preserve:
- exact character identity
- existing three-quarter-back camera
- 4-head chibi proportions
- long blue-green/mint hair
- gray checked long jacket
- dark short skirt
- black short boots
- rough monochrome uneven hand-drawn line style
- stool location
- transparent 1448x1086 canvas
- x=0 / y=0 registration

Person + stool only. Do not draw any drum, cymbal, stand or pedal hardware.

## Required simultaneous motion
- RC = right hand (R). Strike the screen-right crash/RC target. Authoritative runtime reference: approximately (1090, 195). Do not strike the screen-left cymbal or RD.
- SN = left hand (L). Strike the snare target at center-left. Authoritative runtime reference: approximately (570, 520). Do not swap hands.

Both contacts occur at the same instant. Move only the required arms/sticks plus the minimum shoulder/torso rotation needed. Keep head, body scale, stool and camera stable.

## Explicit rejection prevention
- NEVER mirror the composition.
- NEVER move RC to screen-left.
- NEVER create a new front-facing character.
- NEVER redraw the whole character from scratch.
- NEVER include fixed drum hardware in the character PNG.
- NEVER reuse historical/wrong-side RC+SN generations.

## Output expectation
Candidate only until binary QA + fixed-drum composite + contact QA + hit/rebound continuity QA pass.
Expected semantic filename: `rc_sn_r_l_hit.png`.

Source masters:
- CHARACTER_ASSET_GENERATION_SPEC.md
- INSTRUMENT_CONTACT_POINTS.json
- ASSET_NAMING_RULES.md
- QA_CHECKLIST_MASTER.json
- REJECTED_ASSET_REGISTRY.json
- FAILURE_PATTERN_REGISTRY.json
