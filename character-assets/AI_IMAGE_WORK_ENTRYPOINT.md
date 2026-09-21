# DTX Drum Flow — Character Image Work Entrypoint

Status: ACTIVE
Purpose: single discovery point for every new chat/device before character-image work.

## Mandatory read order
1. `character-assets/IMAGE_WORK_PREFLIGHT.json`
2. `character-assets/CHARACTER_FAILURE_KNOWLEDGE.json`
3. `character-assets/AI_OPERATION_MASTER_RULES.md`
4. `character-assets/IMAGE_DECISION_POLICY.md`
5. `character-assets/CURRENT_WORK_ORDER.json`
6. `character-assets/CHARACTER_ASSET_PIPELINE.md`
7. `character-assets/LAYER_RULES.md`
8. current geometry / PROGRESS / transaction / baseline files required by the active work order

## Operational rule
Do not begin by selecting an editing technique.
Begin by identifying the requested motion, locating completed donors, visually checking those donors on the fixed drum, and then selecting the least destructive method.

## Persistent improvements now required
- donor-first before mesh
- completed single-action images are reusable motion solutions
- direct donor composite before deformation
- one owner per active body region when combining donors
- AI visual QA after every meaningful donor/mesh/local-edit step
- numeric PASS never overrides visual FAIL
- detector output must be challenged when it contradicts a visually completed donor
- repeated same-class mesh failure forces method change
- one active case remains locked until VERIFIED
- READ_ONLY paired assets remain untouched

## Current case
The active case is defined only by `CURRENT_WORK_ORDER.json`.
Do not infer a different active target from old chat text.
