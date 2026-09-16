# Character / Drum Baseline Lock — 2026-09-16

This file records the user-approved visual baseline before creating further drummer pose variants.

## Drum baseline

- Existing authoritative fixed drum layer:
  `character-assets/layers/drum/drum_base.png`
- Keep its current position, canvas registration, kit layout, and drawing unchanged.
- This remains the fixed drum reference for future character motion.

## Character baseline

The currently approved character drawing is locked as the new visual reference for future pose generation.

Approved image properties:
- source size: 1199 x 1312
- mode: RGB
- SHA-256 of the approved generated PNG: `e5e74f2c32bc7b69348e54ad0be0b960bb754ef84f443172d04904d8e354c39d`

Visual rules locked by user:
- rough, deliberately messy hand-drawn monochrome linework
- long hair
- no ahoge / stray top hair
- plaid/check-pattern long-sleeve top
- pleated skirt
- drum throne/chair included with the character
- chunky lace-up boots and socks
- left-facing rear/side three-quarter composition
- two drumsticks
- do not clean up or smooth the linework
- do not redesign face, hair, clothing, chair, shoes, body proportions, or composition unless explicitly requested
- future variants should change only the body parts required by the drum motion (arms/hands/feet/body lean as needed)

## Working rule

For Luna Say Maybe pose variants:
1. Treat the above character appearance as the master visual baseline.
2. Treat the existing `drum_base.png` as the master drum baseline.
3. Do not regenerate either baseline casually.
4. When producing a motion variant, preserve every unrelated visual detail.
5. Do not split the chair away from the character unless the user explicitly reopens that decision.

This checkpoint exists specifically to prevent later image-generation drift.
