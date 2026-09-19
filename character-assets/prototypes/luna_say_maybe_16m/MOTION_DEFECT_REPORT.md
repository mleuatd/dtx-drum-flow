# MOTION_DEFECT_REPORT

Status: **IN PROGRESS**

## Restore point

Before this motion-quality sweep, the current known-good `main` was preserved as:

- branch: `backup/pre-motion-qa-20260919-2138`
- commit: `a4e3854449e292264192afa63469edf0fb5048af`

Any later fix that makes the runtime worse should be reverted or reconciled against this restore point.

## Strategy

Do not start by redrawing character assets. The order is:

1. Review the existing whole-song runtime QA evidence from M1 through M148.
2. Record only reproducible visual defects in `MOTION_DEFECT_BACKLOG.json`.
3. Classify the cause before changing code, metadata, timing, contact points, or images.
4. Decide the minimum fix.
5. Apply one fix at a time.
6. Re-run the same runtime QA evidence path.
7. Keep only fixes that improve the target defect without introducing regression.

## Existing QA foundation

The repository already contains live/public runtime QA history covering the song in measure blocks, including M1-4, M5-8, M9-16, M17, M18-24, M25-28, M29-40, M41-45, M46, M47, M48-53, M54, M55-67, M68, M69-104, M105-106, M107-135, M136, and M137-148.

The latest recorded M137-148 public runtime result points to run `35443377688` and artifact `public-runtime-qa-35443377688`.

This means the next step is not to rebuild the screenshot system from scratch. The next step is to collect/review those existing artifacts consistently and convert visual findings into defect records.

## Hard rules

- Do not bulk-regenerate character PNGs.
- Do not touch another terminal's active CLAIM.
- Do not modify a formal PNG until a specific defect has a decided image-level fix.
- Prefer metadata/runtime/timing/contact fixes when the image itself is not the root cause.
- If an image edit is necessary, use the existing image-edit master rules and preserve locked body/camera/stool regions.
- Regressions roll back.


## Reproducible repair recipe rule

Every defect record must now include a `repairSpec` **before any repair begins**.

A repairSpec is not a vague note such as "make the motion natural" or "fix the arm." It must be sufficiently explicit that a later AI/terminal can execute the same intent without guessing.

Each repairSpec must state:

- exact source authority: formal path + SHA256 before image work,
- what is absolutely locked,
- what is allowed to change,
- the desired target state,
- numeric/contact/timing requirements where available,
- ordered edit steps,
- PASS/FAIL validation,
- forbidden strategies,
- rollback point,
- the evidence/reason for choosing that repair.

If any of those are unknown, mark the repairSpec `NEEDS_MEASUREMENT` and gather the missing measurement before editing.

### Language rule

Avoid ambiguous wording such as:

- "make it look better",
- "move it naturally",
- "fix the body",
- "match the original",
- "adjust as needed".

Replace it with explicit scope, for example:

> Preserve camera, head, torso, right arm, both legs and stool. Only the left upper arm, elbow, forearm, hand and left stick may change. At hit, the stick tip must reach the authoritative SN contact. At rebound, the same arm must move away from contact while shoulder/body/stool remain registered to neutral. No formal overwrite until the same runtime screenshot event passes again.

The backlog is therefore both:

1. a defect list, and
2. the future executable repair instruction set.

When a visual problem is added, add its reproducible repair recipe at the same time. Do not accumulate a large list of defects with unspecified future fixes.


## Full M1-M148 sweep completion

The current defect-discovery pass is now complete across M1-M148 using the existing final/live/public runtime QA evidence for each measure block.

### Result

- normalized action families reviewed: **30**
- active repair targets: **15**
- action families with no current repair required: **15**
- every active target has a `repairSpec`
- current formal PNGs remain unchanged by this sweep
- rollback authority remains `backup/pre-motion-qa-20260919-2138` at `a4e3854449e292264192afa63469edf0fb5048af`

### Repair order

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

This order prioritizes reusable base actions first, then high-frequency combos, then lower-frequency multi-limb combos. Do not skip directly to a lower-priority combo when an upstream base registration rule is still unresolved unless the higher-priority issue is technically blocked.

### Important exclusions

- The apparently large M17 FT:L hit/rebound screenshot difference was an overlapped next-event capture (the rebound screenshot was already showing the following BD+RC hit). It is not an FT:L asset defect.
- SN:R has a historically discontinuous rebound PNG, but the runtime deliberately holds the approved SN:R hit image during the short rebound phase while retaining `phase=rebound`; final Web QA passed. Treat this as an existing mitigation, not an active defect.

The backlog is now the executable repair authority: process `fixOrder` from top to bottom, fill missing measurements/SHA/contact coordinates, create candidate-only repairs, re-run the same Web QA event, and promote only after regression-free PASS.
