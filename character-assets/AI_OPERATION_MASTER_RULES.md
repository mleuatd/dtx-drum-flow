# DTX Drum Flow — AI Operation Master Rules

Version: 1.0
Status: ACTIVE
Scope: character image edit / repair / QA / promotion

## 0. Role
This is the persistent top-level operating contract for character-image work.
It does not replace existing project rules. It makes them mandatory and orders how they are applied.

Read together with:
- `character-assets/IMAGE_WORK_PREFLIGHT.json`
- `character-assets/CHARACTER_FAILURE_KNOWLEDGE.json`
- `character-assets/CHARACTER_ASSET_PIPELINE.md`
- `character-assets/IMAGE_DECISION_POLICY.md`
- `character-assets/CURRENT_WORK_ORDER.json`
- `character-assets/LAYER_RULES.md`
- baseline / geometry / target transaction / current PROGRESS

## 1. Priority
When rules conflict:
1. latest explicit user instruction
2. CURRENT_WORK_ORDER.json
3. IMAGE_DECISION_POLICY.md
4. this file
5. issue-specific specifications
6. existing playbooks / ledgers / registries
7. historical candidates/logs

GitHub main is the implementation source of truth.

## 2. Resume, never reset
A new chat/device must restore state from latest main and current ledgers.
Do not restart an existing case merely because the chat changed or the same instruction was pasted again.

## 3. One-case-until-verified
When CURRENT_WORK_ORDER selects one case, stay on it until its completion gate is met.
Do not advance to another issue, phase, or paired image unless explicitly authorized.

## 4. Core image principle
Preserve already-correct finished work.
Before deciding how to edit, decompose the target into:
- primary action
- secondary actions
- protected/static regions
- phase

The primary action must not be degraded merely to add a secondary action.

## 5. Method priority
Use the least destructive method that can satisfy the target:
1. completed approved donor unchanged
2. completed donor + completed secondary donor
3. completed donor + minimal local compositing
4. local seam/contact correction
5. bone-local transform
6. local mesh
7. local AI image edit of the existing source/candidate only
8. large-scale reconstruction only as a last resort

A lower-priority method requires a concrete reason why higher-priority methods cannot work.
Do not choose mesh merely because a prior attempt used mesh.

## 6. Donor-first reasoning
Treat an approved/VERIFIED/PASS donor as a completed motion example, not raw material.
Preserve its contact, stick direction, hand/wrist/elbow/shoulder relationship and body orientation whenever possible.
Before warping a completed donor, visually inspect the donor itself on the fixed drum.

## 7. No new image generation
Text-to-image and whole-character regeneration are prohibited.
AI image editing, if used, must edit the existing approved image/candidate locally and preserve identity, composition, camera, clothing, drum registration and unrelated regions.

AI visual QA is separate from AI image editing and remains required.

## 8. Fixed regions
Avoid unnecessary changes to head, hair, face, torso, pelvis, stool, drum kit and background.
The drum kit remains a locked separate layer whenever possible.

## 9. Contact-first, not stick-extension
For struck instruments:
1. correct instrument
2. correct strike point
3. natural stick tip contact
4. standard/credible stick length
5. natural hand→wrist→forearm→elbow→shoulder chain

Never solve reach by abnormally extending the stick.
Move/reselect the limb geometry or donor instead.

## 10. QA loop
After every meaningful edit step:
EDIT
→ render candidate
→ fixed-drum composite
→ numeric QA
→ AI visual QA
→ classify PASS/FAIL
→ correct only the classified cause

Do not stack several transformations and inspect only at the end.

## 11. Numeric QA is not visual approval
Workflow success, file existence, SHA match and numeric PASS do not prove visual correctness.
Formal/runtime promotion requires visual inspection of the actual candidate and fixed-drum composite.

## 12. Visual hard-fail examples
FAIL on any visible:
- double/banded arm
- detached or duplicated limb
- disconnected hand/stick
- bent/broken/abnormally long stick
- wrong apparent instrument/contact
- transparent hole
- ghost donor geometry
- rectangular splice
- shoulder/elbow/wrist anatomical break
- duplicate leg/foot
- broken leg→ankle→foot→pedal continuity
- protected-region regression

## 13. Fail by cause, not by repetition
After FAIL, classify the cause (donor selection, alignment, contact, joint geometry, mesh artifact, blend boundary, AI edit artifact, registration, transition, protected-region regression, etc.).
Do not indefinitely repeat the same failed strategy.
Reusable lessons must be written to CHARACTER_FAILURE_KNOWLEDGE.json before the next retry.

## 14. Phase and pair safety
If paired asset is READ_ONLY, it may be inspected but never modified.
Do not advance rebound before hit is accepted when the case is hit-gated.

## 15. Promotion
Candidate != formal.
Formal/runtime promotion is allowed only when required:
- numeric PASS
- AI visual PASS
- fixed-drum visual PASS
- transition PASS where applicable
- no protected-region regression
- inspected bytes/path/SHA are reconciled
- latest main rechecked

## 16. Speed
Optimize speed without removing QA:
- reuse completed donors
- operate on the smallest ROI
- reuse immutable inputs
- automate numeric QA/review-sheet creation
- avoid unnecessary ZIP/artifact/workflow churn
- prefer direct local candidate iteration before expensive repository-wide steps
- at equal quality, choose the faster reproducible method

## 17. Completion reporting
Do not report completion merely because a candidate or QA file exists.
Report completion only when the active work order reaches VERIFIED/DONE.
