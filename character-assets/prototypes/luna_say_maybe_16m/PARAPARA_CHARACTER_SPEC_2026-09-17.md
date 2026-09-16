# Luna Say Maybe 1-4 measures parapara character spec (2026-09-17)

## Current scope
This image-refresh pass is intentionally limited to measures 1-4. Do not extend the new character-image set to measures 5-8 until the user explicitly approves the 1-4 result.

Source of truth remains GitHub main plus:
- site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json
- site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json

For measures 1-4 the required action keys are:
- SN:L
- HH:R
- BD:RF
- BD+RC:*

## Required person-frame set
Minimum person-only frame count for measures 1-4: **9 PNGs**.

1. neutral
2. SN:L_hit
3. SN:L_rebound
4. HH:R_hit
5. HH:R_rebound
6. BD:RF_hit
7. BD:RF_rebound
8. BD+RC_hit
9. BD+RC_rebound

The fixed drum layer is separate and is not included in the 9-person-frame count.

## State timing
neutral -> hit -> rebound -> neutral

- hit: 0-90ms
- rebound: 90-170ms
- neutral: 170ms onward when there is no nearer next note
- if the next note is under 90ms away: hit -> next hit
- if the next note is 90-170ms away: hit -> rebound -> next hit
- if the next note is 170ms or more away: hit -> rebound -> neutral

Keep the intentionally slightly choppy hand-drawn flipbook feel. Do not add smooth interpolation.

## Approval gate
The currently generated combined person+drum image is **REFERENCE_DRAFT only**. It is not an approved neutral runtime asset and must not replace the current runtime PNG yet.

Do not commit generated character PNGs as final runtime assets and do not switch the public runtime to them until the user gives an explicit go-ahead after visual review.
