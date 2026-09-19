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
