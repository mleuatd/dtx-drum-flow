# Character image guide - Luna 1-4 (2026-09-17)

> Work handoff priority: read `WORK_HANDOFF_M1_4_2026-09-17.md` first. The newest user-approved neutral is the only visual origin. Deleted legacy pose PNGs must never be restored or reused.


## Visual reference
Use the latest user-approved-direction reference from this chat for:
- camera angle
- body orientation
- head/face direction
- overall seated pose
- rough black-and-white hand-drawn line quality
- long hair silhouette
- jacket/skirt/socks/chunky lace-up boots motif

The latest reference is a **layout/style reference**, not a final layer asset, because the drum kit is drawn into the same image.

## Layer separation
Final character PNGs contain:
- character
- stool/chair

Final character PNGs must NOT contain:
- drum kit
- cymbals
- drum stands/hardware belonging to the fixed kit
- background
- lane/UI/effects

The drum kit remains the fixed independent layer:
- character-assets/layers/drum/drum_base.png

Do not redraw, move, mirror, resize, or bake the drum kit into person frames.

## Registration
All person frames:
- 1448x1086
- transparent background
- x=0
- y=0
- same scale
- same canvas position
- same facing direction

## Difference policy
Treat neutral as the exact visual origin. Variants should look like the same drawing with only the necessary limb movement.

Keep as fixed as possible:
- head position/size
- torso
- waist/hips
- thighs
- boots
- stool
- hair volume
- character scale and canvas registration

Permitted movement:
- upper arm / forearm / wrist
- stick angle
- right-foot pedal motion
- slight shoulder tilt
- slight torso lean

No full-body redraw feeling, no missing stool, no body-proportion jump, no hair redesign, no mirroring.
