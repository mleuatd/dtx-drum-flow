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
