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

## 14. Video-derived appearance model + chibi retarget rule

When a user-provided 360-degree character video is used as a new appearance authority, separate appearance from motion.

Authoritative specification:
`character-assets/prototypes/luna_say_maybe_16m/VIDEO_TO_CHIBI_REFERENCE_MODEL_SPEC.md`

Current profile:
`tools/reference_model/profiles/luna_video_multiview_v1.json`

Mandatory model split:
- video-derived model owns appearance, outfit, hair family/length, multiview silhouette and proportion observations,
- existing DTX limb/action/contact/fixed-drum data owns motion semantics and instrument contact,
- target runtime proportion is 4.0 heads unless a later approved profile supersedes it,
- AI may assist landmark extraction or constrained rendering but may not freely reinterpret outfit, hair, camera, limb side, contact target or proportions,
- a monocular rotating video is treated as a normalized multiview reference, not guaranteed metric 3D,
- cowlick and line-style deterministic post-processors remain downstream authoritative tools.



## 15. Runtime pose tool-authority rule

For runtime character-frame production, numeric/relational facts are resolved before any AI rendering.

Mandatory order:

`fixed drum -> authoritative contact point -> limb/action/phase -> runtime registration -> numeric joint/reach constraint -> 4-head retarget constraint -> appearance constraint -> AI candidate -> deterministic cowlick -> deterministic line style -> fixed-drum composite QA -> transition QA -> Web runtime QA`

Authority split:
- tools own fixed-drum registration, contact targets, limb side, camera family, stool/pelvis anchors, joint topology, reachability, hit/rebound/neutral semantics, 4-head scale, collision/registration checks and PASS/FAIL;
- AI is only a constrained renderer for appearance and local line interpolation inside those numeric constraints;
- hit must satisfy exact stick/pedal contact within the configured tolerance;
- rebound must move naturally away from hit contact and must not be forced back onto the hit target;
- failed AI candidates receive numeric correction instructions, not vague aesthetic retry instructions;
- tool/debug/candidate outputs remain non-formal until fixed-drum and runtime QA pass.

Current implementation authority: `tools/runtime_pose/`.

## 16. Autonomous source-resolution / Dropbox bridge rule

Do not ask the user to manually re-upload, move, rename, or re-identify an image merely because the current terminal cannot immediately hand GitHub bytes to an image-edit renderer.

Before declaring an image task BLOCKED for missing source bytes, the terminal must autonomously exhaust the available repository/connector bridge paths in this order:

1. refresh latest GitHub `main` and read the formal asset path + SHA256,
2. search the project Dropbox bridge by exact SHA256/prefix, formal filename, and known canonical aliases,
3. verify Dropbox metadata against the GitHub formal identity; filename similarity alone is never authority,
4. request Dropbox preview/fetch/download-link capability where available,
5. if direct renderer handoff still cannot be created, record the exact technical boundary in the parallel ledger,
6. split any independent bridge verification, artifact inspection, metadata reconciliation, or visual QA work into `PARALLEL_WORK_LEDGER.json` as `AVAILABLE_FOR_OTHER_TERMINAL` before stopping,
7. continue every non-blocked tool/QA/CI/documentation task on the current terminal.

User-side manual file handling is a last resort, not the default workflow.

Dropbox policy:
- Dropbox is a transport/bridge and provenance aid, not the formal authority.
- GitHub `main` formal path + SHA256 remains the identity authority.
- A Dropbox file may be used only after its bytes/identity are reconciled to the formal GitHub asset.
- Do not replace exact-byte verification with visual resemblance.
- Do not regenerate an asset merely because a connector cannot directly hand bytes to the renderer.
- When a workaround is discovered, record it in the master rule / playbook / ledger so later terminals reuse it instead of asking the user again.

Coordination policy:
- if a bridge or verification subtask can run independently, write it to `PARALLEL_WORK_LEDGER.json` first and commit that ledger change before continuing,
- the current terminal must keep progressing on its own unblocked work after delegation,
- delegation itself is never a reason to stop the current terminal.

## 17. Verified Dropbox raw-materialization bridge

When an exact formal PNG is needed as an image-edit parent and GitHub/Dropbox connector APIs cannot directly expose native image pixels to the renderer, use the verified bridge below before asking the user to upload anything:

`GitHub formal path+SHA256 -> Library /Dropbox mount -> files.list exact external file_id -> files.materialize(raw_file) -> local SHA256 verification -> re-expose the verified file into the current conversation -> renderer parent`

Mandatory rules:
- GitHub formal path + SHA256 remains the sole byte-identity authority.
- Dropbox filename, path, preview, file size, and Dropbox `content_hash` are not sufficient proof by themselves.
- Plain aliases may be stale even when their names look canonical.
- For SN:L, the plain Dropbox aliases `sn_hit_l.png` and `sn_rebound_l.png` were proven stale for formal-source use; the exact matching formal bytes were found at `sn_l_hit_contactfix_20260917.png` and `sn_l_rebound_contactfix_20260917.png`.
- If an obvious Dropbox alias fails SHA256, use GitHub blob size/path metadata plus the Dropbox inventory to locate alternate candidates, then materialize and SHA256-verify them.
- `files.read(mode=image_file)` on Dropbox-mounted PNGs may return `Native image pixels were unavailable`; do not loop on this method. Switch to raw materialization.
- Dropbox `fetch` content extraction for PNG is not a renderer bridge; do not loop on unsupported binary extraction.
- After raw materialization, preserve the exact bytes. Do not recompress or transform before SHA verification.
- Conversation attachment/file IDs are session-local transport references only and must never replace formal SHA256 as durable authority.

Current reusable index:
`character-assets/reference-models/luna_video_20260919/runtime_pose_qa/SOURCE_BRIDGE_INDEX_V1.json`

This bridge was verified on 2026-09-19 for formal neutral, SN:L hit, SN:L rebound, and fixed drum without user file handling.

## 18. Hybrid AI + deterministic tool boundary

Do not force all work into deterministic tools. Use the cheapest reliable method for each job.

AI should own:
- visual interpretation and semantic comparison,
- deciding what looks wrong and why,
- choosing the smallest meaningful visual correction,
- candidate image generation/editing when a valid edit target is available,
- pose/style reasoning that is not reducible to stable numeric rules,
- failure diagnosis and prioritization among plausible next actions.

Deterministic tools should own:
- SHA256 and exact-byte identity,
- Dropbox/GitHub transport and staging/import,
- manifest/inventory updates,
- contact coordinates and numeric reach math,
- repeatable geometry checks,
- binary/canvas/alpha validation,
- regression tests and mechanical QA,
- repetitive bookkeeping that can be made reproducible.

GitHub remains the coordination/state authority; it is not treated as the AI itself.
Do not build a tool-only pipeline merely because automation is possible.
Do not use AI for simple byte/metadata/math work when a deterministic tool is safer.
Prefer a hybrid handoff: tool evidence -> AI judgment/edit -> tool verification.

