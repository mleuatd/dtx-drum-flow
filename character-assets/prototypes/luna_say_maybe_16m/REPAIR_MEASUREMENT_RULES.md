# REPAIR_MEASUREMENT_RULES

Status: ACTIVE — Numeric RepairSpec V1

## Coordinate system
All coordinates use the source PNG canvas: **1448 × 1086 px**, origin at top-left, x increasing rightward and y increasing downward. Do not measure from a scaled browser screenshot unless it is first transformed back to source-pixel coordinates.

## No invented numbers
If a value has not been measured from current authoritative assets/evidence, store `null`, set the local state/confidence to `NEEDS_MEASUREMENT` / `pending_measurement`, and add a measurement TODO. A visually plausible number is not sufficient.

## Measurement order
1. Verify latest-main source paths and SHA256 for neutral, hit, rebound.
2. Measure active-limb alpha-diff bbox against neutral; expand only enough to include antialias/occlusion pixels, then record as editable ROI.
3. Measure head, torso, pelvis, stool and inactive-limb reference boxes.
4. Measure relevant joint/stick/foot anchor points from source images.
5. Use `INSTRUMENT_CONTACT_POINTS.json` only as contact-center authority. Its current textual tolerances are not numeric, so `tolerancePx` remains null until measured.
6. Measure contact tolerance from the fixed-drum composite and record the evidence/method.
7. Compute silhouette/centroid/bbox metrics from alpha masks.
8. Only after all required numbers exist may state become `READY_FOR_FIX`.

## Hard zero-change constraints
Unless an explicit exception ROI is recorded:
- outsideRoiChangedPixels = 0
- inactiveRegionShiftPx = 0
- stoolShiftPx = 0
- cameraAnchorShiftPx = 0
- locked body bbox shift = 0
- scale drift = 0
- rotation drift = 0
- alpha mismatch outside ROI = 0

## Candidate → formal
Never overwrite a formal PNG to test a repair. Produce a candidate, run source-pixel diff checks, fixed-drum composite QA, the exact runtime event repeat, neighbor-event regression, PC evidence and Xperia-class portrait evidence. Promote only on full PASS.

## Rollback
Primary image rollback: `backup/pre-motion-qa-20260919-2138` / `a4e3854449e292264192afa63469edf0fb5048af`.
RepairSpec rewrite backup: `backup/pre-repairspec-v1-20260920-0508`.
