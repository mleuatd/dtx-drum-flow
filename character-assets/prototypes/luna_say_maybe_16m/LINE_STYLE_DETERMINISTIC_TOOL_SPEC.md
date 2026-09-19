# LINE_STYLE_DETERMINISTIC_TOOL_SPEC

Status: **CURRENT_MANDATORY / IMPLEMENTATION SPEC**  
Updated: 2026-09-19T19:15:00+09:00

## Purpose
Normalize the line-construction style of existing Luna Say Maybe formal character PNGs without generative redraw and without changing semantic image content, pose, camera, identity, registration, or instrument contact.

The operation is a deterministic raster transformation: existing line support is analyzed, its centerline is preserved, and apparent weight/density is expressed through repeated one-pixel-equivalent retracing rather than one thick digital brush.

## Scope and precedence
This spec operates under `IMAGE_EDIT_MASTER_RULE.md`, `CHARACTER_GENERATION_PLAYBOOK.json`, `STYLE_BASELINE_SPEC.json`, and the reject/failure registries. It complements `COWLICK_DETERMINISTIC_TOOL_SPEC.md`.

Cowlick tool owns crown geometry. Line-style tool owns line construction only. The line-style tool must not reinterpret cowlick geometry.

## Non-generative implementation
Forbidden: text-to-image, image-to-image whole-frame redraw, prompt-based redrawing, character regeneration, pose synthesis.

Allowed: deterministic Pillow/NumPy/SciPy/scikit-image processing with fixed parameters/profile data.

## Content preservation
Must preserve the same character identity, face/head direction, head silhouette, hair geometry, cowlick geometry, clothing, torso, limbs, sticks, pose, stool, body scale, camera angle, canvas registration, and fixed-drum relationship.

The tool may modify raster values only for line-style normalization; it may not move semantic contours beyond the profile's centerline displacement limit.

## Extraction and centerline model
1. Composite RGBA visually over white to estimate visual darkness.
2. Extract the existing line support using a profile threshold.
3. Remove only tiny isolated components below the profile minimum.
4. Skeletonize the line support to estimate the original line center.
5. Use local source darkness around the centerline to select how many retrace passes are applied.

## Pencil construction rule
- base line width is exactly 1 pixel-equivalent in the current profile;
- apparent thickness is never made by increasing brush width;
- darker/thicker areas receive additional passes of the same fine line;
- passes use fixed ±1px-scale offsets stored in the profile;
- no runtime randomness is used;
- no solid fill is introduced;
- no new hatching is invented; existing texture is retained conservatively.

## Conservative retrace model
The first implementation is intentionally conservative. It preserves a majority of the source visual darkness and adds deterministic fine-line retraces along the existing source skeleton. Added retraces are hard-constrained to a one-pixel dilation of original line support. This prevents new distant geometry from appearing.

This is preferred over deleting the original artwork and reconstructing the entire character from a skeleton, because full reconstruction could destroy hair texture, clothing hatching, hand detail, and intentional roughness.

## Profile
Current profile: `tools/line_style/profiles/luna_pencil_style_v1.json`.

The profile contains canvas, line threshold, base width, pass offsets, pass alpha, density thresholds, geometry QA limits, safety flags, and deterministic seed.

Profile changes require versioning/review. Do not silently mutate an approved profile to fit a single variant.

## SHA and source safety
`--expected-source-sha256` must be used for formal sources whenever the authoritative SHA is known. SHA mismatch is a hard fail. Source and output paths must differ. Formal images are never overwritten by the normalization command.

## QA
`verify_line_style_normalization.py` checks at minimum source/output SHA, canvas, changed pixels/bbox, bidirectional skeleton displacement, 1px-tolerant silhouette difference, non-line geometry corruption, line density before/after, thick-brush safety, and verdict.

Hard fail conditions include canvas mismatch, SHA mismatch, source overwrite, profile base width >1, centerline displacement above profile limit, silhouette difference above profile limit, non-line corruption above profile limit, invalid profile, unreadable image, or image damage.

## Determinism
Same source bytes + same profile + same implementation/dependency versions must produce the same output bytes/SHA. No unseeded randomness is permitted.

## Propagation
Every formal source is normalized independently:

`formal A -> candidate A`
`formal B -> candidate B`
`formal C -> candidate C`

Never chain candidate A into B or candidate B into C.

## Cowlick order
Preferred pipeline:

`formal source -> deterministic cowlick patch when required -> deterministic line-style normalization -> QA -> visual review -> formal promotion`

Cowlick geometry is shape authority; line normalization may only adjust the line-construction rendering of that already-fixed geometry.

## Formal promotion
Tool PASS is not formal approval. Candidate output and QA report remain separate until visual review. No bulk formal overwrite occurs during tool-development/smoke-test stage.
