# Luna Say Maybe 1-4 measures parapara character spec (2026-09-17)

## Scope
This pass is strictly measures 1-4.

Source of truth:
- GitHub latest main
- `site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json`
- `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json`

Required action keys, verified expectation:
- SN:L
- SN:R
- HH:R
- BD:RF
- BD+RC:*

Known opening:
- 4.714583 SN:L
- 4.930410 SN:R
- 5.038324 SN:L
- 5.146237 BD:RF + RC:R

## Required person frames
**11 person+stool PNGs total**:
1. neutral
2. SN:L_hit
3. SN:L_rebound
4. SN:R_hit
5. SN:R_rebound
6. HH:R_hit
7. HH:R_rebound
8. BD:RF_hit
9. BD:RF_rebound
10. BD+RC_hit
11. BD+RC_rebound

The fixed drum layer is separate.

## State timing
neutral -> hit -> rebound -> neutral

- hit: 0-90ms
- rebound: 90-170ms
- neutral: 170ms onward when no closer next note exists
- next gap <90ms: hit -> next hit
- next gap 90-170ms: hit -> rebound -> next hit
- next gap >=170ms: hit -> rebound -> neutral

Keep slight hand-drawn flipbook choppiness. No smooth interpolation.

## Baseline rule
The newest user-approved neutral image from the originating chat is the only valid visual origin for the rebuild. Every variant must be edited from that neutral. Do not use deleted legacy poses as references.

At handoff creation time, the newest approved neutral binary was not yet in GitHub; Work must replace GitHub neutral with the attached/provided latest approved neutral before generating variants.

## Prototype limit
Do not extend the refreshed image set beyond measure 4 in this task.
