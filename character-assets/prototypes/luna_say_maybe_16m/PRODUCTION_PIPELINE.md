# Production Pipeline

Status: CURRENT — Luna Say Maybe character production acceleration layer.

## Recovery order
1. CURRENT_PROJECT_STATE.json
2. M5_PLUS_PROGRESS_LEDGER.json
3. NEXT_IMPLEMENTATION_HANDOFF.md
4. this file
5. PIPELINE_USAGE_POLICY.json

## Mandatory execution entry
Before manually performing a repeatable operation, run:

`node tools/production-pipeline-dispatcher.mjs <task-category>`

Use the returned repository tool/workflow. If the tool cannot be used, record a `MANUAL_OVERRIDE` in the ledger with the skipped tool and reason. Manual duplication without that record is non-compliant.

## Character generation preflight
Before the first character image generation/edit/retry in a session, read `CHARACTER_GENERATION_PLAYBOOK.json` from the rebuilt `PIPELINE_CONTEXT_CACHE.json`.
This is the compact mandatory failure/success memory. Use it instead of rereading every historical ledger. Open the longer FAILURE/REJECTED/contact/transition files only when the current action needs more detail.
No character generation should start until the approved neutral baseline, authoritative limb, target contact side, and relevant high-risk failure checks are resolved.

## Main flow
1. `tools/build-next-asset-queue.mjs` selects production order.
2. Build/derive the hit/rebound pair using approved assets and deterministic local edits whenever possible.
3. Run PRE_RUNTIME lightweight QA only: binary validity, alpha/layer integrity, rejected-asset safety, obvious wrong limb/action, obvious identity/camera corruption, obvious hardware/background contamination.
4. Record contact/diff/centroid/edit-metadata/minor visual concerns as non-blocking signals. Do not micro-tune them before implementation.
5. Formal-save/register the pair and continue immediately to the next READY asset.
6. When every required asset for the contiguous block is formal, update manifest/inventory/mapping and build the provisional runtime block.
7. Capture actual app screenshots on PC and Xperia-class portrait.
8. Perform POST_RUNTIME visual QA for contact, hit/rebound/neutral naturalness, registration, disappearance/jumps, and regression.
9. Repair only assets visibly failing runtime screenshots; keep all others fixed.
10. After screenshot QA passes, promote the contiguous runtimeScope and record COMPLETE_LIVE_QA.

The authoritative timing policy is `M17_QA_PHASE_POLICY.json`.

## Fast Path
Use only when every action key in the range is REUSE_APPROVED and runtimeMapped.
Workflow: `.github/workflows/luna-fast-path.yml`.
Image generation/candidate QA is skipped; chart/limb/mapping/rejected/runtime QA/screenshot/regression remains required.

## Full Path
Use when any action is NEW_IMAGE_REQUIRED, BLOCKED, runtime-pending, or missing mapping.
Workflow: `.github/workflows/luna-full-path.yml`.
It plans missing assets and gates formal save/runtime QA. It does not fabricate or substitute images.

## Visual candidate utilities
Python tools require Pillow when executed.
- `character_candidate_qa.py`: PRE_RUNTIME lightweight mode by default; use `--mode full` only for diagnostic review.
- `build-character-qa-preview.py`: diagnostic preview; not a pre-runtime hard gate.
- `character_image_diff_metrics.py`: diagnostic signal; not a pre-runtime hard gate.

Fine contact and animation naturalness are judged after runtime implementation using actual PC/Xperia screenshots.

## Safety
- REJECTED_ASSET_REGISTRY.json and FAILURE_PATTERN_REGISTRY.json are hard safety inputs.
- BLOCKED images may not be replaced with neutral to obtain a pass.
- live runtimeScope remains unchanged until contiguous block completion gates pass.
- exact limb-aware combo key is preferred over wildcard; wildcard remains backward-compatible fallback.

## Commit boundaries
Follow COMMIT_BOUNDARY_RULES.md. Never combine first-time candidate promotion and runtimeScope expansion.

## Resume
The ledger queue `PRODUCTION_PIPELINE_SPEEDUP` records each SPEED item and commit. Continue the first non-DONE item after reading latest main.
