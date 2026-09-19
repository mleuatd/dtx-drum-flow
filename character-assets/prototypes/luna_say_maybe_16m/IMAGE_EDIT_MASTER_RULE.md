# IMAGE_EDIT_MASTER_RULE

Status: **CURRENT_MANDATORY / HIGHEST-LEVEL CHARACTER IMAGE EDIT RULE**  
Scope: all DTX Drum Flow character-image generation, editing, normalization, retry, QA, and promotion work.  
Updated: 2026-09-19T17:52:00+09:00

This file must be read **before every character-image edit**. It is the top-level rule for image-edit behavior. Existing project ledgers, playbooks, failure registries, reject registries, workspace state, transactions, and PROGRESS files remain authoritative for their own state/history; this file defines the common editing policy that applies before those task-specific records are acted on.

## 1. Mandatory read order before any image edit

1. `character-assets/prototypes/luna_say_maybe_16m/IMAGE_EDIT_MASTER_RULE.md`
2. `character-assets/prototypes/luna_say_maybe_16m/CHARACTER_GENERATION_PLAYBOOK.json`
3. `character-assets/prototypes/luna_say_maybe_16m/FAILURE_PATTERN_REGISTRY.json`
4. `character-assets/prototypes/luna_say_maybe_16m/REJECTED_ASSET_REGISTRY.json`
5. target workspace / transaction / PROGRESS
6. edit-source image path and SHA
7. reference image(s)
8. explicitly allowed edit region(s)
9. explicitly forbidden edit region(s)

If the current source bytes/path/SHA cannot be identified, do not begin image generation/editing.

## 2. Baseline-to-variant comparison policy

- Always compare **baseline/original -> each single variant** one-to-one.
- Never normalize by chaining variant A -> variant B -> variant C.
- The variant must be brought toward the baseline for identity/style/camera/proportion consistency.
- Never move or redraw the baseline merely to match a variant.
- The baseline controls drawing style, character identity, body proportion, camera/view direction, head silhouette, hair family, clothing identity, stool/body registration, and overall composition.
- Motion-specific differences may remain only where required by the target action/phase.

Canonical policy value: `baseline_to_each_variant_only`.

## 3. Line-construction / drawing-style rule

### Highest-priority line rule

**Never switch to a thick digital brush merely to make a line look thicker.**

Use the same conceptual fine pencil/pen width as the baseline. When a contour must look darker or thicker:

- retrace with the same fine-width line,
- use roughly 3-4 or more passes when needed,
- offset the passes slightly,
- keep them generally aligned in the same direction,
- allow visible hand-drawn wobble and uneven overlap.

The goal is not one thick line. The goal is **multiple fine lines whose overlap produces apparent thickness/density**.

Required qualities:

- rough multi-line construction,
- hand-drawn wobble,
- slightly offset retracing,
- uneven density,
- amateur/handmade looseness,
- monochrome black line art on white/transparent background as appropriate to the asset.

Forbidden:

- vector-like cleanup,
- overly smooth single contours,
- replacement with one thick digital brush stroke,
- flat fill used to simulate line density,
- whole-image cleanup/redraw merely to make the drawing look neater,
- simplifying repeated fine strokes into one polished line.

## 4. Local-edit-first rule

When the requested change is local, do **not** regenerate/redraw the full image.

Preferred workflow for a local correction:

```
source image
-> crop/extract only the target region
-> edit only the local patch
-> composite the patch back at the identical coordinates
-> compare pixels outside the allowed edit region
```

When technically possible, require:

`outside_allowed_edit_region_changed_pixels = 0`

If a tool cannot guarantee a local edit, treat that as a strategy limitation. Do not silently convert a local repair into a whole-character redraw.

## 5. Cowlick / crown rule

Current fixed geometry requirements:

- exactly two cowlick strands,
- one resembles katakana `ヘ`,
- the other resembles the mirrored `ヘ`,
- roots are close together,
- both strand tips land back onto the hair,
- no tip may terminate floating in the air,
- a small triangular negative space remains between the two strands,
- the lower strand sits slightly lower,
- the triangular gap should be relatively narrow but must not disappear,
- no solid fill,
- line density is built from repeated fine strokes.

Forbidden cowlick interpretations:

- V shape,
- U shape,
- merely two unrelated lines,
- one strand splitting into two,
- floating tips,
- any freely invented replacement geometry.

Priority for cowlick work:

1. lock geometry from the authoritative cowlick reference,
2. preserve that geometry,
3. adapt only the line quality/density to match the baseline style.

Do not alter the reference geometry merely because another interpretation looks stylistically convenient.

## 6. Reference-image scoping rule

Never use a reference image as vague "inspiration."

For every reference, explicitly state:

- what must be copied/checked,
- what must **not** be imported from the reference.

Example for a cowlick reference:

Use only:
- cowlick geometry,
- cowlick line density / repeated-fine-stroke construction.

Do not import:
- face,
- body,
- pose,
- overall composition,
- camera angle,
- head direction,
- unrelated hair shape,
- instruments or background objects.

A reference may be authoritative for one local property while being forbidden as a source for all unrelated properties.

## 7. Mandatory pre-edit checklist

Before every image edit, confirm at minimum:

1. this `IMAGE_EDIT_MASTER_RULE.md`,
2. `CHARACTER_GENERATION_PLAYBOOK.json`,
3. `FAILURE_PATTERN_REGISTRY.json`,
4. `REJECTED_ASSET_REGISTRY.json`,
5. target transaction,
6. target PROGRESS,
7. source image path / SHA,
8. reference image(s),
9. allowed edit region(s),
10. forbidden edit region(s).

Do not begin editing while any mandatory task-specific item is unresolved unless the ledger explicitly marks it optional.

## 8. Failure-learning policy

A new failure must be recorded **before the next retry**.

For reusable failures, `FAILURE_PATTERN_REGISTRY.json` should record, where applicable:

- failure id,
- actionKey,
- phase,
- observed problem,
- cause,
- prohibited strategy,
- next permitted strategy,
- evidence,
- updatedAt.

For candidate-specific forbidden bytes/paths, also update `REJECTED_ASSET_REGISTRY.json`.

If a recovery rule is reusable beyond the one failed asset, promote it into `CHARACTER_GENERATION_PLAYBOOK.json` and record the rule change in `EDIT_RULE_UPDATES.json`.

Required learning flow:

`new failure -> FAILURE_PATTERN_REGISTRY -> validated reusable recovery -> CHARACTER_GENERATION_PLAYBOOK -> EDIT_RULE_UPDATES`

Never erase prior failure history. Append, supersede, or annotate while preserving evidence.

## 9. Post-edit learning review

After an image-edit task finishes, explicitly check whether there was a new reusable lesson.

Update as needed:

- `FAILURE_PATTERN_REGISTRY.json`,
- `CHARACTER_GENERATION_PLAYBOOK.json`,
- `EDIT_RULE_UPDATES.json`,
- `REJECTED_ASSET_REGISTRY.json` for exact forbidden candidates.

No update is required if no new rule or failure was learned, but the check itself is mandatory.

## 10. Concurrency / GitHub safety

GitHub `main` is the coordination authority.

Before any write affecting these rules or their task ledgers:

- refresh/re-read latest `main`,
- preserve changes made by other terminals,
- reconcile instead of overwriting newer content,
- never force-push,
- do not touch unrelated files,
- do not modify audio/drum-sound work as part of image-rule maintenance.

If another terminal advances the same file, re-fetch the newest file and re-apply only the intended additive changes.

## 11. Workspace inheritance

Every character-image edit workspace must reference this file as its highest-level common rule.

Workspace-specific style, geometry, action, transaction, and QA rules may add constraints, but they may not silently weaken these master protections. If a workspace appears to conflict with this file, preserve both records and resolve the conflict explicitly before editing.
## 12. Deterministic cowlick-tool rule

For crown/cowlick normalization, do not default to free-form generative image editing.

Mandatory preferred path:

`formal PNG -> tools/cowlick/apply_cowlick.py -> profile JSON -> candidate -> outside-ROI pixel QA -> visual review -> promotion`

Authoritative implementation specification:

`character-assets/prototypes/luna_say_maybe_16m/COWLICK_DETERMINISTIC_TOOL_SPEC.md`

Current profile:

`tools/cowlick/profiles/luna_3q_back_left_v1.json`

Rules:
- generative-AI full-frame redraw is prohibited for this operation,
- the source SHA must be known before execution,
- the formal source must never be overwritten directly,
- outside-ROI changed pixels must be exactly zero,
- the profile is versioned data; geometry changes require a new/reviewed profile revision,
- the user-provided 360-degree reference video is calibration provenance, not a per-run free-form reference,
- candidate success does not equal formal promotion; visual review remains required.

## 13. Deterministic line-style normalization rule

For global character line-style normalization, free-form image generation is prohibited.

Mandatory preferred path:

`formal PNG -> tools/line_style/normalize_line_style.py -> tools/line_style/verify_line_style_normalization.py -> candidate + QA -> visual review -> promotion`

Authoritative specification:

`character-assets/prototypes/luna_say_maybe_16m/LINE_STYLE_DETERMINISTIC_TOOL_SPEC.md`

Current profile:

`tools/line_style/profiles/luna_pencil_style_v1.json`

Rules:
- semantic content, pose, identity, camera, silhouette, stool and registration must remain unchanged,
- base line width is fixed to one fine stroke,
- apparent thickness/darkness must come from repeated fine retraces with small deterministic offsets,
- thick digital brush replacement, vector cleanup and new solid fill are forbidden,
- each formal source is processed independently; candidate chaining is forbidden,
- known formal SHA must be verified before processing,
- tool PASS does not authorize formal overwrite; visual review is a separate gate.

