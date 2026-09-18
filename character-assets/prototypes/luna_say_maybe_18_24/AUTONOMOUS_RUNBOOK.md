# Luna Say Maybe M18-24 - Idempotent Autonomous Runbook

This is the authoritative execution instruction for measures 18-24 character assets.
Every new chat must read this file and PROGRESS.json from branch work/luna-m18-24-character-assets first.

## Definition of DONE
Continue from the first unfinished phase until M18-24 is implemented, tested, visually QA'd in the real public browser, and durable evidence is committed.
DONE requires: required assets completed/reused; PNG SHA256/size persisted; manifest/mapping/runtime updated; validations/tests/build pass; safe integration without force-push or touching externally-owned M17 work; Pages/public runtime checked; relevant M18-24 timings visually inspected; screenshot/evidence recorded; PROGRESS.json DONE.

## Sources of truth
Current explicit user instruction > this RUNBOOK > PROGRESS.json > verified GitHub/Dropbox files/hashes > latest main for shared code.
Never reconstruct durable state from chat history.

## Idempotency and anti-loop
- Re-running the same command must be safe.
- Never redo DONE phases when outputs exist/hash-match.
- Never recreate a verified Dropbox working copy.
- Never repeat a BLOCKED investigation unless retryWhen became true or capabilities/files/connections changed.
- If BLOCKED is unchanged, skip that operation, execute every independent metadata/mapping/test-preparation task possible, persist results, and stop only when no executable task remains.
- A run with no durable progress must not rewrite the ledger just for timestamps.
- REJECTED images are permanent negative evidence and must not be reused.
- Never fresh-redraw when verified-source editing is required.
- Ask for user upload only after all acquisition routes are exhausted and ledger says USER_INPUT_REQUIRED.

## State machine
PENDING -> SOURCE_VERIFIED -> EDIT_READY -> GENERATED -> STATIC_QA_PASSED -> PERSISTED -> MAPPED -> RUNTIME_QA_PASSED -> DONE.
Failures: REJECTED or BLOCKED.
BLOCKED records code, investigated, retryWhen, independentWorkCompleted, requiredNext.

## Startup algorithm
1. Verify branch.
2. Read this RUNBOOK and PROGRESS.json.
3. Check latest main/head/divergence; never force push.
4. Verify Dropbox area/files referenced by current phase.
5. Verify hashes/size.
6. Find first non-DONE phase.
7. If BLOCKED, evaluate retryWhen before retrying anything.
8. Execute all possible work through the state machine.
9. Commit durable progress frequently.
10. Re-read ledger after writes.

## Image source rule
Source-derived edits require the actual verified PNG binary as image-editor input. Preview/description/name/thumbnail/memory is insufficient.
Acquisition order: current real attachment; Dropbox binary materialized as editor-addressable attachment; GitHub identical binary materialized as attachment; other materialization route with SHA verification.
If exhausted, mark USER_INPUT_REQUIRED/BLOCKED. Never generate a lookalike.

## Current M18-24 new candidates
BD+RD:RF/R hit/rebound; RD+SN:R/L hit/rebound; BD+HH:RF/R hit/rebound; HH+SN:R/L hit/rebound.
Reuse and authoritative chart/limb sources remain in PROGRESS.json.

## Persistence gate
For accepted images record assetKey/phase/source hash/output SHA256/dimensions/Dropbox formal path/GitHub path/QA evidence. Use established Git data binary flow where needed. Update manifest/mapping/status and validate before advancing.

## Runtime integration and test gate
After required assets exist: update only relevant runtime mappings/inventory; preserve completed earlier measures and isolated M17; run character validation, repository validation, relevant runtime tests and build; commit/push safely; check deploy; open actual GitHub Pages runtime; exercise representative M18-24 times for every new/reused action and hit/rebound/neutral transition; verify layering, limb/action, missing assets, mirroring/redraw and runtime errors; capture screenshots/equivalent browser evidence when capture tooling exists; record tested timestamps, evidence, workflow results and defects.
Static PNG inspection alone is not runtime QA.

## Connection loss/new chat
If a connector is disconnected, do not guess. Persist the exact blocked operation when possible. If durable sources cannot be reached, report which connector must be reconnected. After reconnection the identical command resumes from this runbook and ledger.

## Completion
Do not stop at image generation, commit, or unit tests. Continue through implementation, deploy, real-runtime visual QA and evidence whenever tools permit. Declare completion only when Definition of DONE is satisfied.
