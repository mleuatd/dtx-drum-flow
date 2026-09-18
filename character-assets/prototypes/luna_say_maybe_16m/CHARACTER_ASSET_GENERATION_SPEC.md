# Character Asset Generation Spec

Status: CURRENT. Read before every new Luna Say Maybe character generation/edit.

## Immutable visual identity
- Same approved character identity as `layers/character/base/neutral.png`.
- Long blue-green / mint hair.
- Gray check long jacket, dark short skirt, black short boots.
- Approximately four-head chibi proportions.
- Monochrome rough hand-drawn line art; uneven amateur-like strokes.
- No color, shading, gradient, rendered background or decorative scene.
- Person + drum throne only. Never bake drum/cymbal/pedal hardware into the character layer.
- Transparent 1448x1086 PNG.
- Registration x=0, y=0; no translation, scaling, mirroring or cropping.

## Camera lock
- Large back/three-quarter-back view.
- Face slightly toward screen-left; gaze toward screen-right.
- Back of head and long hair occupy left-to-center.
- Over-opposite-shoulder view; camera comes from behind and wraps toward the character's left.
- Fixed drum extends toward screen-right.
- No front view, pure profile, flat rear view or horizontal mirror.

## Editing rule
The approved neutral is the identity/registration baseline. Existing approved related hit/rebound frames may be secondary references.
Do not redraw the whole character when only an arm/leg/shoulder needs to move.
Keep head, torso scale, stool, clothing silhouette and long-hair mass as stable as physically reasonable.

## Allowed per-action changes
Only the limbs, sticks, minimum shoulder/torso rotation and foot/leg mechanics required by the authoritative actionKey.
Hit: limb reaches the exact instrument contact region.
Rebound: partial natural recovery from hit, not an unrelated pose and not an immediate full neutral reset.

## Forbidden
Different face/character, different camera, realistic proportions, different clothes, colored art, drum hardware in character layer, wrong-side instrument, mirrored pose, unexplained body/stool translation, candidate/rejected source reuse.

## Standard generation/edit template
Use this semantic template when image generation is available:

"Edit the exact approved Luna Say Maybe neutral character layer. Preserve identity, camera, proportions, hair, clothing, stool and 1448x1086 registration. Keep monochrome rough uneven hand-drawn line art and transparent background. Person + stool only; do not draw any drum/cymbal/pedal hardware. For ACTION_KEY=<ACTION_KEY>, PHASE=<hit|rebound>, move only the authoritative limbs and minimum necessary shoulder/torso/leg motion. Target the instrument locations defined in INSTRUMENT_CONTACT_POINTS.json. For hit, make the correct limb/stick/foot clearly reach the target. For rebound, derive naturally from the accepted hit and partially recover without changing camera or identity. Never mirror or crop."

## Acceptance
Generation output is only a candidate until QA_CHECKLIST_MASTER.json passes required binary, identity, purity, limb, contact and transition checks.
