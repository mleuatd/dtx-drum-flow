# Neutral style lock — Luna measures 1-4 (2026-09-17)

## Status
The newest neutral image approved by the user in the originating chat is the visual master.

Important: at the time this document was updated, its newest binary had not yet been committed to GitHub. Work must receive/attach that image and commit it as:
`character-assets/layers/character/base/neutral.png`

Once committed, that GitHub file becomes the sole neutral source of truth.

## Locked style
- monochrome rough line art
- many overlapping/scribbly strokes
- deliberately hand-drawn and imperfect
- visible rough/hesitation/construction feeling
- do not clean into polished digital line art
- no color fill
- no gradients
- 4-head-ish chibi proportion
- long hair
- plaid long jacket
- dark pleated skirt
- socks
- chunky lace-up boots

## Pose
Neutral is an ordinary drummer ready position:
- both hands naturally hold sticks
- neither hand is in a strike
- no dramatic motion
- person + stool only

## Fixed identity/geometry
Do not change:
- camera/body direction
- head position/size
- face placement
- torso/waist
- thighs
- boots
- stool
- hair silhouette/volume
- character scale
- canvas position

## Layer separation
Character neutral contains person + stool only.
The drum remains:
`character-assets/layers/drum/drum_base.png`

Never bake the drum into the character PNG.

## Variant rule
All future hit/rebound frames must be direct minimal edits of this neutral, changing only necessary limbs/sticks/right-foot motion.
