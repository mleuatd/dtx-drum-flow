# Luna Say Maybe approved-pose rescue / prototype status — 2026-09-16

## Current source-of-truth status

- GitHub main head before this note: `cef62831d4e7c114acfdd4bf0c69236d7eb7615d`
- `approved/pose_01.png`: already committed earlier.
- `approved/pose_03.png`: committed at `cef62831d4e7c114acfdd4bf0c69236d7eb7615d`.
- Six additional user-approved generated PNGs from the current chat have been recovered/materialized for binary registration.
- Do not regenerate these approved images merely because Git transport is incomplete.

## Continuous prototype range with the currently approved pose set

The current approved pose set is sufficient to cover measures 1 through 16 continuously.

Measure 17 introduces new tom motion not covered by the current approved set:
- LT
- FT

Therefore the intended prototype cut is now measures 1-16, not 1-4 or 1-8.

## Next steps

1. Finish binary registration of every recovered approved PNG under this prototype's `approved/` directory.
2. Record exact pose-to-animation-key mapping.
3. Wire the approved pose set into the fixed drum + character + effect + note/lane stack.
4. Prefer precomputed limb metadata where available.
5. Run playback QA for measures 1-16.
6. Commit/push and verify the public page.
7. Only after user approval of the 1-16 prototype, resume generating new LT/FT and later-song variants.

No further image generation is required for the 1-16 prototype.
