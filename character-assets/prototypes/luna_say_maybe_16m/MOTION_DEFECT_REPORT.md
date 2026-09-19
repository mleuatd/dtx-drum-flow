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
