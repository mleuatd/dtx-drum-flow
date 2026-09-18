# Character Asset Production Pipeline

This is the reusable M25-148 path. It exists to prevent chat/session/tool boundaries from becoming project blockers.

## Principle

GitHub main is authoritative. Dropbox is durable candidate/recovery storage. PROGRESS.json is the resume cursor.

Do not restart analysis or regenerate a PASS asset. Resume from the first incomplete stage.

## Stages

1. PLAN — resolve actionKey/limb/phase and select an APPROVED parent asset.
2. SOURCE_LOCK — record parent path, exact SHA-256, dimensions, and immutable regions.
3. EDIT — create only the required performance-motion change. The editor used may vary by session; the contract does not.
4. CANDIDATE_SAVE — immediately persist candidate bytes to Dropbox with attempt number.
5. CANDIDATE_IMPORT — use candidate-staging + import-character-review-candidates.yml to import exact verified bytes as review-only.
6. STATIC_QA — PNG/dimensions/alpha/source-diff/left-right/contact/composite checks.
7. VISUAL_QA — inspect character + locked drum composite. Existence-only checks are insufficient.
8. APPROVE — only a PASS candidate may be promoted to formal layers and inventory.
9. RUNTIME — update frame/phase mapping and contiguous runtime scope.
10. PUBLIC_QA — exact deployed SHA, PC 1280x900, Xperia 384x864, hit/rebound/neutral screenshots and runtime errors.
11. CHECKPOINT — write evidence to PROGRESS before moving to the next pair.

## Editor independence

The pipeline must not assume one transport mechanism into an editor. A source may live in GitHub/Dropbox, but the durable contract is its SHA-256 plus canonical path. If a session cannot perform EDIT, all other stages remain usable and the resume cursor stays at EDIT; do not redo PLAN/SOURCE_LOCK.

Never weaken source identity to work around an editor boundary. No screenshots, JPEG/WebP, resized, mirrored, or SHA-mismatched substitutes.

## Pair transaction

Each action pair is a transaction:

hit EDIT -> Dropbox -> rebound EDIT -> Dropbox -> import -> static/composite QA -> approve -> inventory -> PROGRESS -> commit/push.

Do not batch ten unsaved images.

## PROGRESS cursor

Use:
- actionKey
- phase
- attempt
- stage
- parentPath / parentSha256
- dropboxPath
- candidateSha256
- dimensions
- qaStatus
- formalPath
- formalCommit
- updatedAt

Allowed stages: PLAN, SOURCE_LOCK, EDIT, CANDIDATE_SAVE, CANDIDATE_IMPORT, STATIC_QA, VISUAL_QA, APPROVE, RUNTIME, PUBLIC_QA, DONE, BLOCKED_EXTERNAL.

BLOCKED_EXTERNAL is allowed only when the missing capability is outside this repository. Repository/workflow defects must be repaired and retried.

## Existing reusable infrastructure

Prefer these generic components over adding per-measure one-off workflows:
- .github/workflows/import-character-review-candidates.yml
- .github/workflows/import-character-asset-from-dropbox.yml
- .github/workflows/mirror-character-assets-to-dropbox.yml
- .github/workflows/luna-candidate-qa.yml
- .github/workflows/luna-block-qa.yml
- .github/workflows/runtime-character-qa.yml
- tools/character_candidate_qa.py

Legacy per-block builders remain historical evidence; do not copy them for every new measure unless a genuinely unique deterministic transformation is required.
