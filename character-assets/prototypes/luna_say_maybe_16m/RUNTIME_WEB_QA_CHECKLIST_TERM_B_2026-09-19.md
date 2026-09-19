# RUNTIME WEB QA CHECKLIST — TERM-B

Generated: 2026-09-19T20:39:00+09:00
Task: OTHER-003
Target: https://mleuatd.github.io/dtx-drum-flow/

## Screenshot sequence per actionKey

1. Load the public GitHub Pages app and Luna Say Maybe chart.
2. Capture prep immediately before the target note/group.
3. Capture hit at the target contact.
4. Capture rebound after hit.
5. Capture post/neutral recovery.
6. For dense passages, capture the next rapid transition as well.
7. Repeat the same target on PC 1280x900 and Xperia-class 384x864.

## Required visual checks

- Character remains the same identity/camera/body scale/stool registration.
- Correct limb is used.
- Correct instrument and screen side are contacted.
- Contact aligns with INSTRUMENT_CONTACT_POINTS / fixed drum registration.
- No drum/cymbal/pedal pixels leak into the character layer.
- Hit -> rebound -> neutral is continuous and natural.
- No disappearance, body jump, camera jump, or stale frame.
- Rapid transitions do not show the previous action incorrectly.

## Required runtime checks

- manifest/inventory/runtime mapping resolve the intended actionKey and phase.
- asset warning count = 0.
- init error count = 0.
- console/page error count = 0.
- Previous completed blocks remain unchanged unless explicitly intended.

## Evidence record

For each checked actionKey record: commit SHA, actionKey, measure/time, device viewport, prep/hit/rebound/post resolved asset, screenshot filenames/artifact ID, runtime errors/warnings, PASS/WARN/FAIL, and repair target if FAIL.

## Current issue awareness

The master checklist documents a known class of promotion failure where a promoted hit/rebound pair lacks prep:neutral, producing an initialization error. Every newly promoted action must therefore explicitly verify prep resolution before public runtime QA.

This file prepares the QA procedure only; it does not claim a live browser observation was performed in this TERM-B task.
