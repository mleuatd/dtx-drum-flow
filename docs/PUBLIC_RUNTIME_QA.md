# Public Runtime QA

This repository verifies the deployed GitHub Pages runtime with a real headless Chromium browser. Static HTTP/source checks are not accepted as public runtime QA.

## Flow
1. main changes deploy through `.github/workflows/deploy-site.yml`.
2. deployment writes `site/build.json` with the exact commit SHA.
3. `Runtime Character QA` polls the public `build.json` with a 12 minute timeout and starts only when it matches the workflow commit.
4. Playwright opens the public site with `?qa=1`, waits for the app and character runtime, seeks representative chart events, checks hit/rebound/neutral state, image loading, browser errors, and saves screenshots plus `runtime-qa.json`.
5. Evidence is uploaded as a GitHub Actions artifact. A state mismatch, missing image, asset warning, init error, or wrong drum image is FAIL.

## QA hook
`?qa=1` exposes `window.__DTX_CHARACTER_QA__.snapshot()`. It is opt-in and does not alter normal rendering. The snapshot contains current time, measure, animation key, phase, frame, limbs, runtime scope, asset/init warnings, and image load dimensions.

## Reuse for later measures
The runner accepts `MEASURE_START`, `MEASURE_END`, and comma-separated `QA_ACTIONS`. Workflow dispatch exposes measure range and actions so M25-32 through M148 can reuse the same implementation.

## Evidence / anti-loop
The artifact `public-runtime-qa-<run id>` contains `runtime-qa.json` and screenshots for PC and Xperia-like portrait viewports. On failure, inspect the failed job/log and JSON before retrying. Do not rerun an unchanged failing commit repeatedly; record the failed step/error and make a corrective commit first.

## 2026-09-20 — Generic explicit transition QA
- Visual Integrity Batch Runtime QA now resolves the requested actionKey from chart + limb/inventory authority instead of hard-coding BD:RF timestamps.
- It checks PC and Xperia-class portrait for neutral -> hit -> rebound -> neutral using a clean-gap occurrence and exact runtime frame mapping.
- Current verification target: BD+RD:RF/R.
