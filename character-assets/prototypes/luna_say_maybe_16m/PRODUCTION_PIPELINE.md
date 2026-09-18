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
2. `tools/build-character-generation-prompt.mjs` creates the exact hit/rebound edit instruction.
3. For rebound, `tools/derive-rebound-instruction.mjs` derives motion from the accepted hit.
4. Candidate receives `tools/character_candidate_qa.py`.
5. `tools/build-character-qa-preview.py` makes fixed-drum composites, vertical neutral/hit/rebound review, and contact overlay.
6. `tools/character_image_diff_metrics.py` flags suspicious whole-frame/registration changes.
7. `tools/build-staging-json.mjs` creates the single pair transfer record.
8. `tools/prepare-registration-plan.mjs` produces the formal-registration step plan.
9. ACTION_KEY_ASSET_MAP / manifest / inventory / ledger are updated only after gates pass.
10. `tools/build-block-start-checklist.mjs` and `tools/build-qa-sampling-and-risk.mjs` prepare block QA.
11. `tools/build-qa-summary.mjs` compresses QA evidence.
12. `tools/build-next-chat-handoff.mjs` creates a copy/paste continuation command.

## Fast Path
Use only when every action key in the range is REUSE_APPROVED and runtimeMapped.
Workflow: `.github/workflows/luna-fast-path.yml`.
Image generation/candidate QA is skipped; chart/limb/mapping/rejected/runtime QA/screenshot/regression remains required.

## Full Path
Use when any action is NEW_IMAGE_REQUIRED, BLOCKED, runtime-pending, or missing mapping.
Workflow: `.github/workflows/luna-full-path.yml`.
It plans missing assets and gates formal save/runtime QA. It does not fabricate or substitute images.

## Visual candidate utilities
Python tools require Pillow when executed. They never modify the source PNG:
- character_candidate_qa.py
- build-character-qa-preview.py
- character_image_diff_metrics.py

## Safety
- REJECTED_ASSET_REGISTRY.json and FAILURE_PATTERN_REGISTRY.json are hard safety inputs.
- BLOCKED images may not be replaced with neutral to obtain a pass.
- live runtimeScope remains unchanged until contiguous block completion gates pass.
- exact limb-aware combo key is preferred over wildcard; wildcard remains backward-compatible fallback.

## Commit boundaries
Follow COMMIT_BOUNDARY_RULES.md. Never combine first-time candidate promotion and runtimeScope expansion.

## Resume
The ledger queue `PRODUCTION_PIPELINE_SPEEDUP` records each SPEED item and commit. Continue the first non-DONE item after reading latest main.
