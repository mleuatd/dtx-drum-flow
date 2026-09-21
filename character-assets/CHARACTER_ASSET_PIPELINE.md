# Character Asset Production Pipeline

## Mandatory image-failure preflight

Before PLAN, EDIT, candidate generation, retry, VISUAL_QA, or APPROVE on **any character image**, every chat/device MUST begin at:

`character-assets/AI_IMAGE_WORK_ENTRYPOINT.md`

and read the latest-main versions required by `character-assets/IMAGE_WORK_PREFLIGHT.json`, including:
- `AI_OPERATION_MASTER_RULES.md`
- `IMAGE_DECISION_POLICY.md`
- `CURRENT_WORK_ORDER.json`
- `CHARACTER_FAILURE_KNOWLEDGE.json`
- this pipeline
- `LAYER_RULES.md`
- required baseline/geometry/PROGRESS/transaction files

A character-image workflow MUST NOT proceed from an old local/chat copy of those files.

### Decision-before-edit gate

Do not choose mesh, local AI edit, donor splice, or any other technique first.
Before EDIT:
1. resolve primary/secondary actions from the active work order
2. find completed PASS/VERIFIED donors
3. visually inspect the primary completed donor on the fixed drum
4. assign one source owner per active body region
5. try the least-destructive direct donor composite first
6. escalate only when a concrete failure justifies it

### Visual feedback gate

After every meaningful donor composite, local transform, mesh, or local AI edit:
candidate → fixed-drum composite → numeric QA → AI visual QA → classified correction.

Do not perform several geometry edits and wait until the end to look at the image.

Numeric PASS, workflow success, existence, and SHA correctness do not override visual FAIL.

After any image visual FAIL, classify the lesson before the next retry. Action-specific details stay in transaction/PROGRESS; any reusable lesson MUST be added to `CHARACTER_FAILURE_KNOWLEDGE.json` in the same work cycle.

This is the reusable M25-148 path. It exists to prevent chat/session/tool boundaries from becoming project blockers.

## Principle

GitHub main is authoritative. Dropbox is durable candidate/recovery storage. PROGRESS/current work order is the resume cursor.

Do not restart analysis or regenerate a PASS asset. Resume from the first incomplete stage.

## Stages

1. PLAN — resolve actionKey/limb/phase, primary/secondary action and select an APPROVED parent donor.
2. SOURCE_LOCK — record parent path, exact SHA-256, dimensions, immutable regions and region ownership.
3. DIRECT_DONOR_TEST — before destructive deformation, test the completed donor/composite in fixed registration when applicable.
4. EDIT — create only the required performance-motion change using the least destructive method.
5. CANDIDATE_SAVE — immediately persist candidate bytes when durable recovery storage is needed.
6. CANDIDATE_IMPORT — import exact verified bytes as review-only when required.
7. STATIC_QA — PNG/dimensions/alpha/source-diff/left-right/contact/composite checks.
8. VISUAL_QA — inspect actual character + locked drum composite; existence-only checks are insufficient.
9. APPROVE — only a numeric+visual PASS candidate may be promoted.
10. RUNTIME — update frame/phase mapping and contiguous runtime scope.
11. PUBLIC_QA — exact deployed SHA, PC/Xperia screenshots and runtime errors where applicable.
12. CHECKPOINT — write evidence before moving to the next pair.

## Editor independence

The pipeline must not assume one transport mechanism into an editor. A source may live in GitHub/Dropbox, but the durable contract is its SHA-256 plus canonical path. If a session cannot perform EDIT, all other stages remain usable and the resume cursor stays at EDIT; do not redo PLAN/SOURCE_LOCK.

Never weaken source identity to work around an editor boundary. No screenshots, JPEG/WebP, resized, mirrored, or SHA-mismatched substitutes.

## Pair transaction

Do not advance rebound before hit is visually accepted unless the active work order explicitly says otherwise.
A READ_ONLY pair asset may be inspected for transition QA but must not be edited.

## PROGRESS cursor

Use:
- actionKey
- phase
- attempt
- stage
- parentPath / parentSha256
- donor/region ownership
- candidateSha256
- dimensions
- numericQaStatus
- visualQaStatus
- failureClass
- formalPath
- formalCommit
- updatedAt

Allowed stages include: PLAN, SOURCE_LOCK, DIRECT_DONOR_TEST, EDIT, CANDIDATE_SAVE, CANDIDATE_IMPORT, STATIC_QA, VISUAL_QA, APPROVE, RUNTIME, PUBLIC_QA, DONE, BLOCKED_EXTERNAL.

BLOCKED_EXTERNAL is allowed only when the missing capability is outside this repository. Repository/workflow defects must be repaired and retried.

## Existing reusable infrastructure

Prefer generic components over per-measure one-off workflows:
- .github/workflows/import-character-review-candidates.yml
- .github/workflows/import-character-asset-from-dropbox.yml
- .github/workflows/mirror-character-assets-to-dropbox.yml
- .github/workflows/luna-candidate-qa.yml
- .github/workflows/luna-block-qa.yml
- .github/workflows/runtime-character-qa.yml
- tools/character_candidate_qa.py

Legacy per-block builders remain historical evidence; do not copy them for every new measure unless a genuinely unique deterministic transformation is required.
