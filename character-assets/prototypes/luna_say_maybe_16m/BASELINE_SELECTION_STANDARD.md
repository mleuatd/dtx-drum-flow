# Baseline Selection Standard

## Purpose
The newest `main` image set is not automatically the parent. A targeted repair can create unrelated regressions, so parent promotion requires a complete original-resolution audit against a known-good restore point.

## Mandatory procedure
1. Freeze candidate and known-good commit SHAs.
2. Extract the complete `character-assets/layers/character` PNG set from both.
3. Verify relative-path inventory and dimensions.
4. Hash corresponding PNGs. A byte-identical pair may reuse one visual finding only after identity is proven.
5. Open every PNG at original resolution. Inspect every changed pair side-by-side at 1:1 scale. Thumbnails, filenames, JSON state, or old PASS/VERIFIED labels are insufficient.
6. Inspect anatomy, arm/hand/leg count and continuity, stick count/length/grip/angle, action readability, hair/clothing/skirt, stool relation, and residual artifacts.
7. For hit/rebound assets, isolated character layers cannot certify exact drum/cymbal/pedal contact. Fixed-drum composite QA is mandatory before promotion.

## Ledger fields
Each image/version record must store versionId, sourceCommit, index, filename, actionKey, phase, status, severity, defects, defectRegions, repairDifficulty, repairScope, likelyRepairMethod, donorAvailability, estimatedRisk, notes, inspectedAt, and inspectionMethod.

## Parent-selection priority
Prioritize: anatomy integrity; arm-hand-stick continuity; plausible strike trajectory; absence of duplicate limbs; waist/leg/skirt continuity; face/hair/clothing stability; local repairability; donor availability; low regression risk; easy runtime rollback. Do not choose only by raw FAIL count.

## Regression gate after a repair
Compare the candidate against its parent at full resolution. Check outside-ROI changes where applicable, anatomy/stick counts, hit/rebound continuity, and fixed-drum composite contact. Any new HIGH/CRITICAL defect outside the intended repair scope rejects the candidate.

## Promotion conditions
A newer set becomes the standard parent only after a complete full-set audit, no new CRITICAL defects, no unjustified increase in HIGH defects, changed-frame anatomy/stick QA, fixed-drum contact QA, no increase in repair difficulty, and a recorded rollback SHA.

## Rollback conditions
Rollback when a promoted repair creates an extra limb, third leg, duplicate/abnormally long stick, disconnected hand/arm, skirt/stool rectangular splice, instrument penetration, or new HIGH/CRITICAL defect outside the intended scope. Do not keep patching on top of a degraded parent; restore the last audited coherent parent and reapply only the needed local motion delta.

## 2026-09-21 decision
Compared `a4e3854449e292264192afa63469edf0fb5048af` against current snapshot `b298fba62b49599be4fb61b166f429b75df9539e`. All 64 corresponding PNGs were inspected; 35 are byte-identical and 29 differ.

The selected standard parent is `a4e385...`. Its remaining failures are predominantly bounded stick/line residues, whereas the current snapshot has multiple extra-limb, third-leg, and skirt/stool regressions.

Frame 010 (`combo/bd_rc_hit.png`) strongly supports the choice: baseline has coherent two-leg anatomy and a normal right-stick trajectory; current has an extremely overlong right stick plus central third-leg/vertical residue. `rc/hit_r_refresh.png` is not a safe direct donor because it itself has an overlong/doubled-stick defect.
