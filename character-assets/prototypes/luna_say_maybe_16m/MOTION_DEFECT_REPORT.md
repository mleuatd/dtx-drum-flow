## 2026-09-20 — BD+RD:RF/R final runtime close
- Static anatomy, linework, and fixed-drum composite gates had already PASSed from run 35476033283 / artifact 10594885001.
- Public runtime QA run 35477061624 / artifact 10594916218 tested real chart occurrences on PC and Xperia-class portrait with failed=0 / passed=14 and included BD+RD:RF/R at M130.
- Synthetic explicit-sequence failures were rejected as invalid methodology because timeline seeking to invented times cannot inject arbitrary action keys; it selected unrelated real chart events instead.
- BD+RD:RF/R is now VERIFIED.

## 2026-09-20 — Visual Integrity Batch 12
- Reviewed BD+FT:RF/L and BD+FT:RF/R from explicit FRONT evidence (run 35476984329, artifact 10594531751).
- BD+FT:RF/L hit/rebound failed because the left active stick is discontinuous and a detached diagonal outer fragment remains.
- BD+FT:RF/R hit/rebound failed because the right hand carries forked/duplicated stick shafts.
- Both actionKey pairs moved to HOLD_VISUAL_INTEGRITY. Formal PNGs unchanged; runtime QA not entered.

## 2026-09-20 — Visual Integrity Batch 11
- Reviewed BD+HT:RF/L and BD+FT+SN:RF/R/L using explicit FRONT batch evidence (run 35476815322, artifact 10594496614).
- BD+HT:RF/L hit/rebound failed because the left active-stick geometry contains an extra short parallel fragment and rebound grip-to-tip continuity/direction is unreadable.
- BD+FT+SN:RF/R/L hit/rebound failed because the left stick is detached/truncated and the right-hand stick is forked/duplicated.
- Both actionKey pairs moved to HOLD_VISUAL_INTEGRITY. Formal PNGs unchanged; runtime QA not entered.
- Batch Prep concurrency learning: FRONT/BACK now use independent override files so a back-session override cannot silently replace a front-session CLAIM artifact.

## 2026-09-20 — Visual Integrity Batch 10
- Reviewed RC:R and LT+SN:R/L from current-main Batch Prep evidence (run 35476534354, artifact 10593644215).
- RC:R hit/rebound failed because the right hand carries duplicated/parallel stick shafts.
- LT+SN:R/L hit/rebound failed because the right stick is forked/duplicated and the left active-stick path contains detached/truncated line fragments.
- Both actionKey pairs moved to HOLD_VISUAL_INTEGRITY. Formal PNGs unchanged; runtime QA not entered.

## 2026-09-20 — Visual Integrity Batch 09
- Reviewed HT:L and FT+SN:R/L from current-main Batch Prep evidence (run 35476194165, artifact 10593174478).
- HT:L hit/rebound failed because the left active stick is discontinuous and an extra short detached stick-like fragment remains near the hand.
- FT+SN:R/L hit/rebound failed because the left stick is detached/truncated while the right stick is forked/duplicated.
- Both actionKey pairs moved to HOLD_VISUAL_INTEGRITY. Formal PNGs unchanged; runtime QA not entered.

## 2026-09-20 — Visual Integrity Batch 08
- Parallel prep initially mis-selected other-session keys because auto-priority ignored the ledger's active claimed batch. No QA/promotion was performed on those wrong keys.
- Fixed tools/character_layers/prepare_visual_integrity_batch.py so push-triggered prep honors activeVisualIntegrityBatch when its two actionKeys are still CLAIMED.
- Corrected Prep run 35475852782 / artifact 10594059870 selected BD+HH:RF/R and BD+LT:RF/R exactly.
- BD+HH:RF/R failed static hard gates: duplicated/disconnected left arm-hand-stick geometry plus blocky seat/lower-body splice.
- BD+LT:RF/R failed static hard gates: duplicated/crossing right-hand active-stick geometry.
- Both pairs moved to HOLD_VISUAL_INTEGRITY; formal PNGs unchanged; runtime QA not entered.

## 2026-09-20 — Visual Integrity Batch 07
- Reviewed FT:R and FT:L from current-main Batch Prep evidence (run 35475676709, artifact 10594034740).
- FT:R hit/rebound failed because the right-hand active stick is duplicated into two divergent shafts.
- FT:L hit/rebound failed because the left stick is broken/discontinuous with a detached diagonal fragment.
- Both actionKey pairs moved to HOLD_VISUAL_INTEGRITY. Formal PNGs unchanged; runtime QA not entered.

## 2026-09-20 — Visual Integrity Batch 06
- Reviewed LT:L and BD+SN:RF/R from current-main Batch Prep evidence (run 35475549511, artifact 10594285311).
- LT:L hit/rebound failed static hard gates due duplicated/discontinuous left-hand stick geometry and a detached stick-like segment.
- BD+SN:RF/R hit/rebound failed static hard gates due disconnected right-hand/stick continuity plus a detached floating curved artifact line.
- Both actionKey pairs moved to HOLD_VISUAL_INTEGRITY. Formal PNGs unchanged; runtime QA not entered.

## 2026-09-20 — Visual Integrity Batch 05
- Reviewed RC+SN:R/L and LT:R from current-main full-resolution Batch Prep evidence (run 35475413657, artifact 10593488275).
- RC+SN:R/L hit/rebound both failed static hard gates because a horizontal/rectangular splice cuts through lower hair/torso geometry and remains visible over the fixed drum.
- LT:R hit/rebound both failed static hard gates because the right-hand active stick reads as duplicated/crossing two-stick geometry.
- Both actionKey pairs moved to HOLD_VISUAL_INTEGRITY. Formal PNGs were not changed. No minimal retry was attempted because these are structural failures; runtime QA was not entered.

## 2026-09-20 — Visual Integrity Batch 04
- Reviewed RD:R and BD+SN:RF/L from current-main full-resolution Batch Prep evidence (run 35475145116, artifact 10593238245).
- RD:R hit passed static visual review; rebound failed anatomy/linework/composite due a hard rectangular splice through hair/torso and right forearm/hand-stick geometry. Pair moved to HOLD_VISUAL_INTEGRITY; formal PNGs unchanged.
- BD+SN:RF/L hit failed due large blocky splice across lower hair/skirt/seat plus left-stick truncation; rebound failed due a hard rectangular left-stick dropout near the hand. Pair moved to HOLD_VISUAL_INTEGRITY; formal PNGs unchanged.
- No minimal retry was attempted because these are structural hard-gate failures, not light/local defects. Runtime QA was not entered.

## 2026-09-20 — Visual-integrity batch 03: SN:L + BD+RC:RF/R

- Batch prep workflow: 35474616622; artifact: 10593307774; exact current-main formal bytes.
- SN:L hit: anatomy / linework / fixed-drum composite static review PASS.
- SN:L rebound: FAIL — duplicated/disconnected arm-hand-stick geometry, three-stick silhouette, and whole-body/head/stool registration discontinuity. Pair is HOLD_VISUAL_INTEGRITY; runtime QA blocked.
- BD+RC:RF/R hit/rebound: FAIL — disconnected/duplicate upper-right arm-hand-stick plus blocky vertical splice through body/seat/lower-body continuity. Pair is HOLD_VISUAL_INTEGRITY; runtime QA blocked.
- These are large structural failures, not light/local defects, so no minimal retry was consumed in this batch. Formal PNGs were not modified.

## 2026-09-20 — Visual Integrity Batch 02 closure

- BD:RF hit/rebound: human anatomy, linework, fixed-drum composite, and public runtime neutral -> hit -> rebound -> neutral QA all PASS. Runtime workflow 35473367417; artifact 10593426362. Status promoted to VERIFIED.
- HH:R hit/rebound: static visual hard gate FAIL. One alpha-safe minimal retry also failed; formal PNGs remain unchanged and both frames stay HOLD_VISUAL_INTEGRITY.
- HH:R retained defects: horizontal/rectangular splice across shoulder/hair, incoherent arm/forearm overlap, blocky splice residue, and rebound stick/arm dropout.
- No force push; historical evidence/candidates preserved.

## 2026-09-20 Visual-integrity 2x4 batch 02 — BD:RF + HH:R static review

- BD:RF hit/rebound: full-resolution current-main static review PASS for anatomy, linework, and fixed-drum composite. Runtime transition remains pending; no formal PNG rewrite in this review step.
- HH:R hit/rebound: hard FAIL. Horizontal/rectangular splice cuts shoulder/hair; arm linework remains incoherent; rebound also shows stick/arm dropout.
- One minimal alpha-safe retry was generated only as QA evidence; it still FAILed and was not promoted.
- Visual QA run: 35472780085, artifact 10593056465. Retry run: 35472957167, artifact 10593926080.
- Promotion remains blocked for all four until required gates are satisfied; HH:R is HOLD.

# MOTION_DEFECT_REPORT

Status: **NUMERIC REPAIR SPEC V1 READY / MEASUREMENTS PENDING**

## Restore points
- Image/runtime restore: `backup/pre-motion-qa-20260919-2138` @ `a4e3854449e292264192afa63469edf0fb5048af`
- RepairSpec rewrite restore: `backup/pre-repairspec-v1-20260920-0508`

## What changed
All current active defects now use **RepairSpec V1**, a machine-readable repair contract. The previous narrative intent is retained under `legacyNarrative`, but repair execution is governed by numeric fields.

A repair may not begin merely because the intended limb or visual symptom is known. It must first have source identity, pixel ROI, locked regions, relevant anchors, contact targets/tolerance, motion constraints, bbox/silhouette metrics, runtime timing, validation targets and rollback authority.

## Numeric field meanings
- `editableRoisPx`: the only source-pixel rectangles allowed to change.
- `exceptionRoisPx`: explicit narrowly-scoped exceptions; empty by default.
- `lockedReferenceRegions`: body/camera/stool regions that must retain registration.
- `anchorPointsPx`: relevant joint, stick, foot, seat and head reference points.
- `contactTargetsPx`: instrument target center + limb + role + measured tolerance.
- `motionConstraints`: global zero-drift and registration limits.
- `limbSpecificConstraints`: joint/contact/rebound angle and length limits for active limbs.
- `staticBodyBoundingBoxes` / `activeLimbBoundingBoxes`: source-pixel boxes used for diff and registration checks.
- `silhouetteMetrics`: alpha/centroid/IoU checks.
- `runtimeTiming`: current authoritative phase timing converted to milliseconds.
- `validation.measurableChecks`: machine-checkable PASS/FAIL targets.

## Unmeasured coordinates
Unknown values are never guessed. They are represented as `null` with `NEEDS_MEASUREMENT` / `pending_measurement`. A defect remains non-executable until all numbers required for that repair are measured.

## ROI outside-change rule
Default: `forbidOutsideEditableRoi = true`, `outsideRoiChangedPixelsAllowed = 0`. Camera, stool, inactive body/limb registration, scale and rotation also have a default allowed shift/drift of zero. If a physical overlap truly requires collateral pixels, an explicit measured `exceptionRoisPx` entry is required before editing.

## Contact error
`INSTRUMENT_CONTACT_POINTS.json` supplies current contact centers (HH 190,390; SN 420,535; BD 735,650; HT 575,360; LT 885,455; FT 1165,535; RC 1215,145; RD 965,250). Its tolerance descriptions are currently non-numeric; therefore every `tolerancePx` stays `null` / `NEEDS_MEASUREMENT` until measured from fixed-drum composite evidence. No radius may be invented.

## Inactive-region shift
Inactive region, camera anchor, stool and locked-body bbox shift target: **0 px**. Nonzero movement is a hard FAIL unless the region was first reclassified into an explicit active/exception ROI.

## Runtime timing authority
Current `POSE_TRANSITION_RULES.json` maps to:
- prep: 0 ms
- hit: 180 ms
- rebound: 100 ms (180→280 ms)
- neutral recovery window: 280 ms
- rapid-repeat maximum gap: 90 ms

## Candidate → formal promotion
1. Source path/SHA verified.
2. Required ROI/anchors/bboxes/tolerances measured.
3. Candidate created without modifying formal PNG.
4. Pixel diff satisfies zero-change constraints.
5. Fixed-drum composite contact check passes.
6. Same runtime QA event passes.
7. Neighbor regression count is 0.
8. PC evidence passes.
9. Xperia-class portrait evidence passes.
10. Only then promote candidate to formal.

## Fix order
The existing order remains authoritative because it stabilizes reusable base actions before dependent combos:
1. SN:L
2. HH:R
3. BD:RF
4. RD:R
5. HT:R
6. BD+HH:RF/R
7. HH+SN:R/L
8. BD+RC:RF/R
9. RC+SN:R/L
10. BD+RD:RF/R
11. RD+SN:R/L
12. BD+SN:RF/L
13. BD+HH+SN:RF/R/L
14. BD+HT:RF/R
15. BD+RC+SN:RF/R/L

## Repair execution flow
1. Select defect.
2. Read RepairSpec.
3. Verify source SHA.
4. Verify/measure ROI, anchors and contacts.
5. Create candidate.
6. Fixed-drum composite QA.
7. Runtime QA.
8. Neighbor regression QA.
9. PASS → promote.
10. FAIL → rollback and update measurements/spec.

## Current completion state
The **schema rewrite is complete for all active defects**, but actual geometry/tolerance measurements are intentionally not fabricated. Therefore each active defect remains `NEEDS_MEASUREMENT` until its null ROI/anchor/bbox/contact-tolerance fields are populated. Formal PNGs are unchanged by this specification rewrite.


## Exact raster measurement pass (2026-09-20)

All 15 active repair targets were measured from the exact PNG bytes on GitHub main via `REPAIR_MEASUREMENTS_AUTO.json`.

Recorded per action:
- exact neutral/hit/rebound SHA256,
- opaque-pixel count,
- opaque bounding box,
- opaque centroid,
- neutral→hit changed pixels / ratio / diff bbox / diff centroid / alpha mismatch,
- neutral→rebound equivalents,
- hit→rebound equivalents,
- bbox IoU,
- centroid shift in pixels,
- authoritative instrument contact centers,
- distance from each contact center to the nearest changed pixel (diagnostic proxy, not stick-tip contact error).

These values are copied into each active defect's `repairSpec.measuredGeometry`, `silhouetteMetrics`, and `validation.measurableChecks.currentObserved`.

### Important distinction

The exact full-frame diff bbox is **not** automatically promoted to `editableRoisPx`. A defective frame can contain whole-body drift; treating that large observed diff as an editable ROI would authorize the very corruption the repair is intended to remove.

The remaining null fields are semantic measurements (joint anchors, limb-only ROI, stick-tip/foot contact error and contact-radius tolerance). They require landmark/limb segmentation or playing-surface calibration and are intentionally not guessed.


## Visual Integrity QA Gate (2026-09-20)

The motion-repair system now treats **human anatomy**, **linework integrity**, and **fixed-drum composite semantics** as mandatory promotion gates.

Changed-pixel count, ROI containment, SHA identity, alpha, bbox, centroid, camera registration and other numeric checks remain required, but they are no longer sufficient for PASS by themselves.

A candidate is a hard FAIL if any of the following remains visible:
- pelvis -> thigh -> knee -> shin -> ankle -> foot/boot continuity is unreadable or anatomically implausible,
- shoulder -> elbow -> wrist -> hand continuity is unreadable,
- seated posture or front/back limb order is physically incoherent,
- a drum stick is broken, interrupted, disconnected from the hand, malformed, or points/ends unnaturally,
- unexplained line artifacts remain around waist / pelvis / skirt / seat,
- line dropout, double stroke, isolated line, or layer-derived stray line corrupts the silhouette,
- the fixed-drum composite contradicts strike, pedal, seat-contact, or front/back semantics,
- a frame looks acceptable alone but becomes anatomically or semantically wrong when composited with the approved fixed drum.

The formal rules are:
- `QA_CHECKLIST_MASTER.json` schemaVersion 2
- `VISUAL_INTEGRITY_QA_RULES.md`
- `VISUAL_DEFECT_TAXONOMY.json`
- `MOTION_DEFECT_BACKLOG.json` schemaVersion 4

### Promotion policy

Existing candidate files, QA evidence, runtime screenshots and historical repair evidence are preserved. Their existence does **not** grandfather an asset into VERIFIED / APPROVED_LIVE.

Promotion now requires explicit PASS for:
1. human anatomy QA,
2. linework QA,
3. fixed-drum composite QA,
4. runtime-transition visual coherence,
5. existing numeric / ROI / regression checks.

Until all mandatory axes pass, the target remains in a pending review state.

### Current reclassification

| Issue | Action | Current status |
|---|---|---|
| MOTION-001 | SN:L | NEEDS_VISUAL_REVIEW |
| MOTION-002 | BD+RC:RF/R | NEEDS_VISUAL_REVIEW |
| MOTION-003 | BD:RF | NEEDS_HUMAN_ANATOMY_QA |
| MOTION-004 | RC+SN:R/L | NEEDS_VISUAL_REVIEW |
| MOTION-005 | BD+HH:RF/R | NEEDS_VISUAL_REVIEW |
| MOTION-006 | BD+RD:RF/R | NEEDS_VISUAL_REVIEW |
| MOTION-007 | HH:R | NEEDS_VISUAL_REVIEW |
| MOTION-008 | HH+SN:R/L | NEEDS_VISUAL_REVIEW |
| MOTION-009 | RD+SN:R/L | IN_FIX |
| MOTION-010 | RD:R | IN_FIX |
| MOTION-011 | BD+RC+SN:RF/R/L | NEEDS_VISUAL_REVIEW |
| MOTION-012 | HT:R | NEEDS_VISUAL_REVIEW |
| MOTION-013 | BD+HT:RF/R | NEEDS_VISUAL_REVIEW |
| MOTION-014 | BD+SN:RF/L | NEEDS_VISUAL_REVIEW |
| MOTION-015 | BD+HH+SN:RF/R/L | NEEDS_VISUAL_REVIEW |

### BD:RF priority review

`BD:RF` is the highest-priority anatomy review target. Both hit and rebound remain blocked from VERIFIED / APPROVED_LIVE until review confirms:
- pelvis-to-thigh continuity,
- knee/ankle bend direction,
- foot/boot connection,
- seat/pelvis/leg overlap,
- right-foot bass-pedal semantics,
- fixed-drum composite coherence.

### RepairSpec impact

All 15 repair specs now include mandatory visual-integrity requirements and measurement TODOs for relevant landmarks such as hip, pelvis, knee, ankle, foot, toe, boot connection, seat edge/contact, shoulder, elbow, wrist, hand, stick grip continuity and stick-tip contact.

A low changed-pixel ratio, zero outside-ROI changes, or stable bbox/centroid can support a PASS, but can never override an anatomy, linework, or composite FAIL.

## 2026-09-20 2x4 visual-integrity batch 01

- Scope: `SN:L` hit/rebound + `BD+RC:RF/R` hit/rebound (4 frames).
- `SN:L hit`: exact-source masked edit attempted via Actions run `35471764688`; BLOCKED before image edit because repository workflow lacks `OPENAI_API_KEY`. Diagnostic artifact: `10592983884`. No candidate image produced and no formal image changed.
- `SN:L rebound`: prior repaired/formal evidence preserved; new anatomy/linework/fixed-drum/runtime-transition hard gates remain pending.
- `BD+RC hit/rebound`: existing method2 deterministic machine QA rechecked and remains PASS. Both have 0 outside-mask changed pixels and 0 locked head/torso/stool/left-leg guard changes. These numeric checks are insufficient for visual-integrity promotion, so both remain pending visual review.
- Result: batch recorded as PARTIAL_BLOCKED; no visual-integrity promotion and no force push.
