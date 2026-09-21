## 2026-09-21 — One-image adaptive strike repair pipeline
- Standardized one-image repair order: CURRENT_STATUS -> source authority -> registration -> active limb chain -> adaptive contact mode -> optional strike expression -> linework cleanup -> fixed-drum composite -> transition -> final decision -> GitHub record.
- Added REPAIR_PIPELINE_PATTERNS.json with REGISTRATION_FIRST, TIP_OR_SHAFT_CONTACT_ADAPTIVE, LIMB_CHAIN_BEFORE_STICK_EXTENSION, CONTACT_THEN_LINEWORK_CLEANUP, OPTIONAL_STRIKE_EXPRESSION, FIXED_DRUM_COMPOSITE_REQUIRED, TRANSITION_REQUIRED, MINIMUM_CHANGE_WINS and FAILED_METHOD_LEARNING.
- Added STRIKE_CONTACT_QA_RULES.json. Tip contact and shaft contact are both valid; neither is mandatory. The chosen mode must look natural and minimize destructive edits.
- Added processing-cost preference (FAST/NORMAL/HEAVY) so equal-quality solutions prefer the lighter method.
- DMR-009 hit remains the only active image for this experiment; no second image may start before its result is recorded.

## 2026-09-20 09:16 JST — Shared HOLD repair workflow
- All terminals must read HOLD_REPAIR_PLAYBOOK.json and latest MOTION_DEFECT_BACKLOG before editing.
- FRONT claims the lowest available MOTION issue; BACK claims the highest available issue. Claimed items are untouchable by other terminals.
- Repair unit is the hit/rebound pair. Machine QA alone never promotes; both phases require full-resolution anatomy/linework/fixed-drum PASS, then real-chart runtime QA on PC/Xperia.
- A local repair that machine-PASSes but still fails human pair review is re-diagnosed at pair level and returned to HOLD with exact learning, not repeatedly patched.
- RD+SN and RD:R learning from the interrupted session is recorded in the playbook.

## 2026-09-20 — Verify BD+RD:RF/R
- Closed BD+RD:RF/R after static visual PASS plus real public runtime QA PASS across PC and Xperia-class portrait.
- Recorded synthetic explicit-sequence failures as invalid test methodology because arbitrary action keys cannot be synthesized by timeline seek alone.
- Runtime evidence: run 35477061624 / artifact 10594916218.

## 2026-09-20 — Visual Integrity Batch 12
- Claimed and statically reviewed BD+FT:RF/L and BD+FT:RF/R.
- Both pairs failed structural stick-continuity hard gates and moved to HOLD_VISUAL_INTEGRITY; formal PNGs remain unchanged.
- Evidence: workflow run 35476984329, artifact 10594531751.

## 2026-09-20 — Visual Integrity Batch 11
- Completed FRONT review of BD+HT:RF/L and BD+FT+SN:RF/R/L after reconnect.
- Both pairs moved to HOLD_VISUAL_INTEGRITY for structural stick-continuity failures; formal PNGs remain unchanged.
- Added independent FRONT/BACK batch override support to prevent parallel Prep evidence from selecting the wrong queue.
- Evidence: workflow run 35476815322, artifact 10594496614.

## 2026-09-20 — Visual Integrity Batch 10
- Claimed and statically reviewed RC:R and LT+SN:R/L as the next front-queue 2x4 batch.
- Both pairs failed structural stick-continuity hard gates and moved to HOLD_VISUAL_INTEGRITY; formal PNGs remain unchanged.
- Evidence: workflow run 35476534354, artifact 10593644215.

## 2026-09-20 — Visual Integrity Batch 09
- Claimed and reviewed HT:L and FT+SN:R/L after reconciling parallel-session HOLD/CLAIM state.
- Both pairs failed structural stick-continuity hard gates and moved to HOLD_VISUAL_INTEGRITY; formal PNGs remain unchanged.
- Evidence: workflow run 35476194165, artifact 10593174478.

## 2026-09-20 — Parallel-safe Batch Prep fix + Batch 08
- Batch Prep now honors the ledger's active claimed 2x4 batch before falling back to auto-priority selection, preventing parallel sessions from preparing another session's frames.
- Discarded one mis-selected evidence artifact without changing its formal assets or status.
- Corrected Batch 08 evidence reviewed BD+HH:RF/R and BD+LT:RF/R; both failed structural visual-integrity gates and moved to HOLD_VISUAL_INTEGRITY.
- Formal PNGs remain unchanged.

## 2026-09-20 — Visual Integrity Batch 07
- Claimed and statically reviewed FT:R and FT:L as the next front-queue 2x4 batch.
- Both pairs failed structural stick-continuity hard gates and moved to HOLD_VISUAL_INTEGRITY; formal PNGs remain unchanged.
- Evidence: workflow run 35475676709, artifact 10594034740.

## 2026-09-20 — Visual Integrity Batch 06
- Claimed and statically reviewed LT:L and BD+SN:RF/R as the next front-queue 2x4 batch.
- Both pairs failed structural visual-integrity hard gates and moved to HOLD_VISUAL_INTEGRITY; formal PNGs remain unchanged.
- Evidence: workflow run 35475549511, artifact 10594285311.

## 2026-09-20 — Visual Integrity Batch 05
- Claimed RC+SN:R/L and LT:R while excluding the active BACK-BATCH-01 keys owned by another session.
- Static QA moved both pairs to HOLD_VISUAL_INTEGRITY: RC+SN has structural hair/torso splice artifacts; LT:R has duplicated/crossing active-stick geometry.
- Formal PNGs remain unchanged; runtime QA was not entered.
- Evidence: workflow run 35475413657, artifact 10593488275.

## 2026-09-20 — Visual Integrity Batch 04
- Claimed and statically reviewed RD:R and BD+SN:RF/L via the 2x4 batch-prep workflow.
- RD:R hit passed; rebound failed structural rectangular splice/cut around hair-torso/right-arm-stick continuity.
- BD+SN:RF/L hit/rebound failed structural splice/stick-continuity hard gates.
- Both actionKey pairs moved to HOLD_VISUAL_INTEGRITY; formal PNGs unchanged and runtime QA was not entered.
- Evidence: workflow run 35475145116, artifact 10593238245.

## 2026-09-20 — Visual-integrity batch 03

- Processed SN:L and BD+RC:RF/R as the next 2-action / 4-frame batch using current-main evidence (workflow 35474616622, artifact 10593307774).
- SN:L hit passed static anatomy/linework/composite review; rebound failed for duplicated/disconnected arm-hand-stick geometry and whole-body registration discontinuity. Pair moved to HOLD_VISUAL_INTEGRITY.
- BD+RC:RF/R hit/rebound failed for disconnected/duplicate arm-stick geometry and blocky vertical body/seat splice. Pair moved to HOLD_VISUAL_INTEGRITY.
- Both failures are structural rather than light/local; no minimal retry was attempted. Formal PNGs were preserved and runtime QA was correctly skipped.

## 2026-09-20 — Visual-integrity batch 02 closure + prep automation

- Closed the 2-action/4-frame batch for BD:RF and HH:R.
- BD:RF hit/rebound passed anatomy, linework, fixed-drum composite, and explicit public runtime neutral->hit->rebound->neutral QA on PC and Xperia portrait (run 35473367417, artifact 10593426362) and are now VERIFIED.
- HH:R hit/rebound remain HOLD_VISUAL_INTEGRITY after one minimal alpha-safe retry failed to remove shoulder/hair splice and right-arm/stick defects; formal PNGs were not overwritten.
- Added `tools/character_layers/prepare_visual_integrity_batch.py` and `.github/workflows/visual-integrity-batch-prep.yml` to auto-select the next two action keys from BRUSHUP_LEDGER priority, verify formal SHA/canvas, and emit character-only, fixed-drum composite, transition-strip, and manifest evidence in one batch.

## 2026-09-20 Visual-integrity 2x4 batch 02 — BD:RF + HH:R static review

- BD:RF hit/rebound: full-resolution current-main static review PASS for anatomy, linework, and fixed-drum composite. Runtime transition remains pending; no formal PNG rewrite in this review step.
- HH:R hit/rebound: hard FAIL. Horizontal/rectangular splice cuts shoulder/hair; arm linework remains incoherent; rebound also shows stick/arm dropout.
- One minimal alpha-safe retry was generated only as QA evidence; it still FAILed and was not promoted.
- Visual QA run: 35472780085, artifact 10593056465. Retry run: 35472957167, artifact 10593926080.
- Promotion remains blocked for all four until required gates are satisfied; HH:R is HOLD.

## 2026-09-20 — Visual Integrity QA Gate for character motion repair

## 2026-09-20 — Visual-integrity 2x4 batch 01

- Processed two action pairs / four frames: `SN:L` hit+rebound and `BD+RC:RF/R` hit+rebound.
- Triggered exact-parent masked `SN:L hit` edit workflow run 35471764688. It stopped at the credential boundary because GitHub Actions has no `OPENAI_API_KEY`; no candidate image bytes were produced.
- Rechecked existing `SN:L rebound` repair evidence and method2 `BD+RC` hit/rebound machine QA. BD+RC hit/rebound remain machine-QA PASS with zero outside-mask changes and locked-region guards unchanged.
- No frame was promoted under the 2026-09-20 visual-integrity policy because human-anatomy, linework, fixed-drum-composite, and runtime-transition visual hard gates are still pending.
- Historical candidates/evidence were preserved; no force push and no formal PNG overwrite occurred.
- Promoted human anatomy, linework integrity, and fixed-drum composite semantics to mandatory character-pose QA gates; changed-pixel/ROI/SHA/bbox/centroid checks remain necessary but are no longer sufficient for PASS.
- Updated `QA_CHECKLIST_MASTER.json` to schemaVersion 2 with explicit hardPass/hardFail criteria for pelvis/leg/joint continuity, seated-pose readability, stick continuity/hand connection, waist/pelvis/skirt/seat artifacts, and fixed-drum strike/pedal semantics.
- Added `VISUAL_INTEGRITY_QA_RULES.md` and `VISUAL_DEFECT_TAXONOMY.json` with first-class defect categories including human_anatomy_break, joint_continuity_break, stick_continuity_break, waistline_artifact_break, line_dropout_break, line_double_stroke_break, and fixed_drum_composite_break.
- Updated `MOTION_DEFECT_BACKLOG.json` to schemaVersion 4. Existing candidates/evidence were preserved, but prior FIXED-like dispositions were reopened for visual-integrity review where explicit anatomy/linework/composite PASS evidence was absent.
- `BD:RF` is now `NEEDS_HUMAN_ANATOMY_QA` and cannot return to VERIFIED / APPROVED_LIVE until pelvis→thigh→knee→ankle→foot/boot continuity, seat overlap, RF bass-pedal semantics, and fixed-drum composite coherence pass.
- Normalized `BRUSHUP_LEDGER.json` so historical live-QA evidence is retained in prior fields while current `qaState` becomes `visual-integrity-pending` whenever mandatory visual gates remain incomplete.
- Broken/interrupted sticks, hand-stick disconnects, unexplained waist/seat lines, anatomically implausible lower-limb structure, and composite-only contact/occlusion contradictions are now hard failures.
- No character PNG bytes were regenerated or overwritten in this policy pass.

## 2026-09-19 — M68 and M69-104 character runtime closure
- Closed M68 `BD+RC+SN:RF/R/L` without regenerating formal bytes. Formal SHA-256 remain hit `0ca0d673e70fd0072ceac0fb6ac8d5b7088a828263e9239d38edb9312cdb163e` and rebound `5584de18ef1d912b377208e805593de37a26cf6946efc41356297cb20836d619`.
- M68 public runtime QA run `35426237555`, artifact `10579760232`: 6/6 PASS across PC/Xperia hit, rebound and neutral recovery; no init/console/page/request errors; screenshots reviewed.
- Expanded reuse-only runtime through M104 with no new character PNGs: M69-104 contains 550 notes / 389 groups / 20 existing action keys, all present in runtimePhaseFrameMap.
- M69-104 public runtime QA run `35426755584`, artifact `10579246619`: 86/86 PASS, runtimeScope `1-104`, no browser/runtime errors; 86 screenshots reviewed with no character disappearance, wrong-person redraw or fixed-drum registration drift.
- M69-104 is DONE; M105-106 is released for the two new deterministic BD+FT pairs.

## 2026-09-19 — M55-67 reuse-only character closure
- Expanded Luna Say Maybe character runtime contiguously through M67 with no new character PNG generation: 194 notes / 129 groups / 17 existing action keys.
- Public Runtime Character QA run `35420829149`, artifact `10576863064`: 70/70 records PASS across PC and Xperia portrait; runtimeScope `1-67`; no asset/init/console/page/request errors.
- Reviewed PC/Xperia contact sheets; no visible character disappearance, wrong-person redraw, or fixed-drum registration drift.
- Verified the conflict-safe generic runtime-QA persistence change in the same run: browser QA, artifact upload, and `Persist generic runtime QA state` all completed successfully.
- Synchronized stale promoted-combo entries in `ACTION_KEY_ASSET_MAP.json` to the already-live runtime inventory so later sessions do not regenerate M18-24/M47 assets.
- M55-67 is DONE; M68 `BD+RC+SN:RF/R/L` is released as the next new pair.

## 2026-09-19 — M54 character runtime QA closure
- Closed Luna Say Maybe M54 `BD+HT:RF/L` without regenerating image bytes. Formal hit/rebound SHA-256 remain `cd343fa52ac0ebe32cd68e8805067f2168800b4cb3b6cd226192f4388cb47fa7` / `13f4076afa68a704f8525b4a78dba8fc6d3b99922a0c77ec823c963d965885c5`.
- Public runtime QA run `35420373297`, artifact `10576732695`: 4/4 PASS (PC hit/rebound + Xperia portrait hit/rebound), runtimeScope 1-54, expected/actual action+frame matched, 1448x1086 character/drum loads OK, no init/console/page/request errors.
- Reviewed the four screenshots; no character/drum registration drift or wrong-character redraw was observed.
- Workflow-level failure was not a browser/runtime failure: `Persist generic runtime QA state` hit a rebase conflict on M54 PROGRESS after another main update. M54 ledgers were closed manually from the uploaded PASS evidence.
- Released M55-67 as the next reuse-only block; no new character image generation is permitted for that range.

## 2026-09-19 — M25-28 HT:R attempt04 rejected through pipeline retry controller
- Re-read latest main after parallel-session updates; preserved all newer M18-24 and pipeline-first changes.
- Found repository-generated HT:R attempt04 on main (hit SHA 824672a7..., rebound SHA 0147a2d9...) built from approved LT:R parents.
- Reproduced the current attempt04 builder geometry against exact approved LT:R parent bytes and fixed drum for visual review. Hard failure remains: the original right-hand stick is still present while a second HT-directed shaft starts from an artificial forward anchor, so the pose has a detached/duplicate stick and is not safe to formalize.
- A further locked-neutral direct-edit retry again returned edit_op=null and redrew the character instead of performing a local edit; the result was rejected and not persisted to project assets.
- Ran the repository character-retry-controller for repeated LOCAL_EDIT_ARTIFACT. Decision: USE_APPROVED_LIMB_PATCH, hardStopSameStrategy=true. Persisted decision at character-assets/prototypes/luna_say_maybe_25_32/RETRY_DECISION_HT_R.json.
- HT:R remains BLOCKED_EXTERNAL until a genuinely registered approved right-arm/right-hand/right-stick patch compatible with locked neutral exists, or a true local image-edit path becomes available. RC:R, FT+SN:R/L and HT:L remain formal. BD+HT remains source-locked and M25-28 runtime expansion remains prohibited.

## 2026-09-19 — M25-28 FT+SN and RC formalized; HT:R edit blocker isolated
- FT+SN:R/L attempt03 exact bytes were imported, then rejected by actual fixed-drum review because the left SN stick missed the calibrated SN contact. Attempt04 changed only the left-stick shaft on the locked-baseline candidate, passed SN/FT contact and transition review, was saved to Dropbox, imported, and promoted exactly in commit 14a9b4449bf97fb99ca2b4c45247a22574c2c57f.
- RC:R current deterministic pair was reproduced from locked neutral with SHA match, fixed-drum visual QA passed, exact bytes were saved to Dropbox, and formal promotion completed in b588a43d9b4c39c986bc2dd3f081d6a7df52215f.
- Formal M25-40 new-asset count is now 6/10 PNGs: HT:L, FT+SN:R/L, and RC:R pairs. HT:R remains the only M25-28 missing pair.
- HT:R was not force-promoted. Two image-edit attempts returned edit_op=null and unrelated new images; deterministic local prototypes attempt06/07/08 also failed visual QA. All failed outputs were rejected and not persisted to project assets.
- HT:R is therefore BLOCKED_EXTERNAL until a true local edit can preserve locked neutral while relocating only right arm/hand/stick. Runtime scope remains M1-24 and BD+HT work remains gated behind HT:R + M25-28 checkpoint.

## 2026-09-19 — M25-28 resume reconciliation
- Re-read GitHub main, Dropbox and M25-28 transactions before continuing; no completed block was restarted.
- Preserved M29 HT:L already formal-promoted by a parallel session; no BD+HT derivation was started because M25-28 is not checkpoint-complete.
- HT:R current pair is attempt03 hit (63d48afb...) + attempt02 rebound (a82a928f...); fixed-drum visual QA still FAILS because the neutral right-arm position forces an implausibly long cross-body HT stick. Formal promotion remains prohibited; next correction must replace/relocate the complete right arm/hand/stick local region from a compatible locked-baseline tom pose.
- RC:R current pair is attempt03 hit (9dc93593...) + attempt02 rebound (8ad6abaf...); duplicate-stick defect is improved but final fixed-drum arm/stick proportion review remains HOLD. Not formalized.
- FT+SN:R/L attempt03 was rebuilt as locked-baseline limb-local composition, exact hit/rebound bytes saved to Dropbox (0aea2d50... / 44f7e791...), and candidate staging exists at character-assets/candidate-staging/m25_28_ft_sn_attempt03.json. Local binary/character QA passed; GitHub candidate import and fixed-drum composite QA remain pending.
- Updated all three M25-28 transactions and PROGRESS.json to the latest attempt state. No runtime mapping/scope expansion was performed.

## 2026-09-19 — Character generation preflight memory
- Added mandatory `CHARACTER_GENERATION_PLAYBOOK.json` as a compact pre-generation memory for character image work.
- Playbook captures recurring failure modes, successful first-attempt heuristics, baseline-parent rules, and the QA retry loop.
- Wired the playbook into `build-pipeline-context-cache.mjs` and `start-pipeline-task.mjs`, so session bootstrap automatically exposes it before character generation.
- Updated pipeline policy, production guide, next-chat bootstrap, and current project state to require the playbook before the first image attempt.
- Long historical ledgers are now secondary references; the compact playbook is read first for speed.

## 2026-09-18 — M9-16 final state reconciliation
- Reconciled stale ledger/queue/handoff fields after successful M1-16 live deployment and QA.
- Confirmed live runtimeScope is 1-16; NIMG-018 through NIMG-023 are complete.
- RC+SN:R/L formal hit/rebound remain the approved live pair; no image regeneration or asset replacement performed.
- Released only the next contiguous queue item, ASSETQ-003 LT:R hit for M17, as READY. M17 image generation was not started.
- Public PC/Xperia runtime QA evidence remains SUCCESS run 35351134562 / artifact 10549284671; validate 35351278979; Character Asset Validation 35351227038; Pages deploy 35351010527.

## 2026-09-18 — Open ledger work exhausted to image blocker
- Swept all non-DONE ledger statuses and materialized `OPEN_WORK_QUEUE.json`.
- Normalized 19 meaningful remaining work items: 1 completed during the sweep, 18 blocked, 0 executable without the missing corrected RC+SN image pair.
- Preloaded approved `BD+SN:RF/L` hit/rebound under an exact runtime key without expanding live runtimeScope; live transition QA remains pending.
- Normalized stale `RC+SN:L/R` wording to authoritative `RC+SN:R/L`.
- Prepared corrected RC+SN hit prompt and rebound derivation instruction.
- Materialized PIPELINE_CONTEXT_CACHE, AUTO_OPTIMIZATION_REPORT and ACTIVE_PIPELINE_SESSION under a documented MANUAL_OVERRIDE because the current connector exposes no direct workflow_dispatch/repo Node execution entrypoint.
- NEXT_ASSET_QUEUE no longer leaves dependent future image tasks as ambiguous TODO; ASSETQ-001 is the explicit current blocker and later entries are dependency-blocked.
- No image was generated, no approved asset was overwritten, and live runtimeScope remains 1-8.

## 2026-09-18 — Mandatory pipeline-first tool usage enforcement
- Added mandatory `PIPELINE_USAGE_POLICY.json/.md`: existing repository tools/workflows are the default execution path, not optional helpers.
- Added `tools/production-pipeline-dispatcher.mjs` to route task categories to required existing tools/workflows before manual work.
- Added `tools/start-pipeline-task.mjs` to create a resumable active-session plan recording required tools for the current task.
- Added `tools/check-pipeline-compliance.mjs` to detect missing required-tool evidence unless a documented `MANUAL_OVERRIDE` exists.
- Updated CURRENT_PROJECT_STATE, PRODUCTION_PIPELINE, NEXT_IMPLEMENTATION_HANDOFF, NEXT_CHAT_COMMAND generator and generated NEXT_CHAT_COMMAND to require dispatcher-first execution.
- Validation now fails if the mandatory policy/dispatcher/current-state integration disappears.
- Manual duplication of an existing tool requires ledger evidence with skipped tool, reason, evidence and follow-up repair/extension.
- No image assets or live runtimeScope were changed.

## 2026-09-18 — Production pipeline speedup complete
- Implemented SPEED-001..025 plus SPEED-026 risk-aware runner integration and SPEED-027 candidate-QA workflow.
- Added automatic next-asset queue, generation/rebound instruction builders, candidate binary QA, fixed-drum/comparison/contact preview, image-diff metrics, staging/lifecycle/registration planning, block checklist/reuse analysis, transition-risk sampling, standardized screenshot naming, QA summary and next-chat command generation.
- Added Fast Path for approved/mapped reuse-only blocks and Full Path for blocks with missing/pending assets; Full Path never substitutes neutral for missing assets.
- Added failure-pattern registry, commit/autonomy rules, production pipeline guide, and production-pipeline validation.
- Production contract validation run 35340578530 SUCCESS.
- Risk-aware M1-8 Luna Block QA run 35340512012 SUCCESS, artifact 10544374908.
- No character image was generated or overwritten; live runtimeScope remains 1-8.

## 2026-09-18 — Luna implementation infrastructure preparation
- Added formal asset naming rules (human + machine-readable), a 30-key action-to-asset mapping master, character generation/edit spec, 11-part instrument contact master, pose transition rules, QA checklist, rejected-asset deny registry, and block completion gates.
- Added one-command `Luna Block QA` workflow/runner with measure range and optional exact actionKey input. It reports missing/BLOCKED assets without substituting neutral, and produces PC/Xperia screenshots plus summary JSON when a range is QA-ready.
- Added backward-compatible exact limb-aware combo mapping support before wildcard fallback, preventing future collisions such as `BD+SN:RF/L` vs `BD+SN:RF/R` while preserving current M1-8 behavior.
- Extended planning validation to enforce master coverage, naming, contact coverage, rejected-runtime safety and live-scope invariants.
- No character images were generated or overwritten; live runtimeScope remains measures 1-8.

> Current-state note (2026-09-18 19:41 JST): this file is historical chronology, not the current-state authority. For current status use `character-assets/prototypes/luna_say_maybe_16m/CURRENT_PROJECT_STATE.json`. Older entries describing runtime 1-4, M5-8 blockers, unfinished RD, or unresolved full-song limbs are superseded by later entries.

## 2026-09-18 — Luna full-song limb assignment authority
- Researched standard right-handed drum-set coordination before extending limb assignments: bass drum under right foot, hi-hat pedal under left foot, right-hand cymbal timekeeping, left-hand snare backbeat, alternating R/L single strokes for rapid/fill passages.
- Upgraded `hand_rules.json` to v2, explicitly adding `LB=LF` and phrase-aware rapid-SN/simultaneous-hit policies.
- Added full-song limb generator and CI validation.
- Promoted `Luna_say_maybe_full_limbs.json` for all 2,158 notes through measure 148.
- Validation: M1-16 mismatch 0, missing limbs 0, simultaneous same-limb conflicts 0, rapid-SN same-hand repeats 0, unresolved groups 0.
- Resolved all 8 known SN+tom conflicts as SN=L + FT/LT=R and 64 rapid-SN phrases with alternating phrase-aware sticking.
- Added limb-aware `FULL_SONG_ACTION_KEY_INVENTORY.json` with 1,527 time groups.
- Corrected runtime LB fallback from RF to LF and switched runtime limb lookup to the authoritative full-song sidecar while keeping character runtimeScope at measures 1-8.
- Added normal validation coverage for the full-song limb sidecar.

## 2026-09-18 — M9-16 reusable existing-asset runtime QA
- Added dedicated QA-only Playwright harness/workflow that intercepts inventory inside the test browser only; public/live runtime remains measures 1-8.
- Exercised every M9-16 occurrence of reusable `BD:RF`, `RD:R`, `SN:L`, `HH:R`, `BD+RC:*`, and formal refreshed `BD+SN:*` at pre/hit/rebound/post on PC 1280x900 and Xperia 384x864.
- Successful run `35331851179`, artifact `10542000517`: frame mismatches 0, load failures 0, asset/init warnings 0, console/page errors 0.
- Manual PC/Xperia contact-sheet review found no visible disappearance, wrong-person pose jump, or fixed-drum registration drift. Final HH:R at 30.829691 returns to neutral after rebound.
- BD+SN core runtime behavior passed at all 14 M9-16 occurrences; do not regenerate it.
- Two transitions remain BLOCKED solely because corrected RC+SN does not exist: `BD+SN@25.434007 -> RC+SN@25.649835` and `RC+SN@25.649835 -> BD:RF@25.865662`.
- First QA run `35331421842` failed only because the harness sampled `naturalWidth=0` during image-src swaps; screenshots still showed the character. Harness commit `17f858b67ed9d67b6a9a5cdcf744dacbf611b148` waits for frame load and the rerun passed.

## 2026-09-18 — M9-16 non-image preparation
- Kept live runtime safely at measures 1-8 while image generation is unavailable.
- Reconciled M9-16 state: approved RD:R refresh pair is reused; corrected BD+SN refresh pair remains formal-layer-saved and visual-QA-passed; corrected RC+SN is the sole missing image pair.
- Verified M9-16 coverage: 83 notes / 65 groups / 0 missing limbs. RC+SN occurs once at measure 13, 25.649835, with SN=L and RC=R.
- Added `M9_16_RUNTIME_EXPANSION_PLAN.json`: target 1-16 scope is 144 notes / 124 groups with runtime keys `SN:L`, `SN:R`, `BD:RF`, `HH:R`, `BD+RC:*`, `RD:R`, `BD+SN:*`, `RC+SN:*`.
- Recorded latest rejected RC+SN regeneration as `CHAR-QA-0007`: unrelated front-facing redraw (`edit_op=null`), never registered. Retry is temporarily blocked by image-generation rate limit.
- Removed the temporary source-export workflow after source recovery; existing Actions artifacts remain as evidence.
- Prepared the remaining image-independent work queue in `M5_PLUS_PROGRESS_LEDGER.json`; resume image-dependent work at NIMG-013 after corrected RC+SN hit/rebound are available.

# Changelog

## 2026-09-18 — M5+ refreshed continuation / progress-ledger pass
- Added `M5_PLUS_PROGRESS_LEDGER.json` to track completed, in-progress, skipped/rejected, runtime-pending and unresolved work by measure block.
- Recorded every current-chat generation attempt with SHA/reason. Rejected: wrong-side RD pair, drum-leaking first BD+SN pair, wrong-side RC+SN pair, unrelated management-sheet misgeneration, and a later front-facing/different-character RD retry.
- Corrected BD+SN hit/rebound were preserved in Dropbox, imported review-only to GitHub, visually QA'd over the fixed drum (run `35321151121`, artifact `10537157014`), then copied to formal layer paths:
  - `character-assets/layers/character/combo/bd_sn_hit_refresh.png`
  - `character-assets/layers/character/combo/bd_sn_rebound_refresh.png`
  Both remain `VISUAL_QA_PASSED_RUNTIME_PENDING`; no runtime mapping yet.
- Added review-only candidate import workflow. Fixed missing Pillow and missing Dropbox secret by supporting per-asset short-lived download URLs. Candidate import succeeded in commit `36a4c7706f2110aa9040f3dedcdf1fff968af8b0`.
- Refactored `site/character-prototype.js` to read runtime measure scope from `asset_inventory.json` instead of hardcoding measure 4. Current inventory remains measures 1-4, so public behavior is unchanged.
- Updated UI contract test for inventory-driven scope and adjusted character asset validation to allow registered later-measure runtime-pending layers while separately enforcing the active M1-4 runtime set.
- Public GitHub Pages redeploy succeeded. Live Playwright runtime QA after the scope refactor succeeded: run `35321917979`, artifact `10536838661`.
- Added full-song limb analysis draft: 1,819 mechanically resolved notes, 195 unresolved notes, 179 rapid-SN notes, 8 same-limb simultaneous conflict groups. Draft remains analysis-only.
- Added later-measure part-combination inventory for measures 17-148: 2,014 notes / 1,403 groups, with no limb guessing.
- Current hard blocker for live expansion remains refreshed RD:R hit/rebound. RC+SN also still needs regeneration. Historical/rejected images are explicitly forbidden from reuse.

## 2026-09-18 — Refreshed Luna M5+ expansion preparation
- Started the requested refreshed expansion from measure 5 onward using completed M1-4 as the absolute visual baseline; the live runtime remains M1-4 until new frames pass QA.
- Recomputed measures 5-8 from FINAL notes + authoritative limb sidecar: 33 notes / 32 groups; only new action key is RD:R.
- GitHub Actions visual QA run 35315598184 / artifact 10535695236 compared the historical RD hit against the refreshed baseline. The historical frame was rejected for different line treatment, proportions, camera/body presentation and registration.
- Recomputed measures 9-16: 83 notes / 65 groups / missing limb assignments 0. New keys beyond approved M1-4 are RD:R, BD+SN:RF/L and RC+SN:L/R.
- GitHub Actions visual QA run 35315877548 / artifact 10535690785 rejected the historical BD+SN and RC+SN hit frames as incompatible with the refreshed baseline.
- Added M5-8 and M9-16 required-asset manifests. Refreshed measures 5-16 require six new direct-edit frames: RD hit/rebound, BD+SN hit/rebound, RC+SN hit/rebound.
- Verified the FINAL chart contains 2,014 notes after measure 16 through measure 148, with no embedded limb/hand/foot metadata. The only precomputed authoritative limb sidecar currently covers measures 1-16; measure 17+ mapping must not guess limbs.
- Added QA issues CHAR-QA-0005 and CHAR-QA-0006. Historical later-measure PNGs remain unapproved and are not wired into refreshed runtime.

## 2026-09-18 — M1-4 live runtime character QA closure
- Added/used Playwright GitHub Actions live-browser QA against the public GitHub Pages build at PC 1280x900 and Xperia-class portrait 384x864.
- Fixed rapid-hit phase timing so rebound can exist between closely spaced notes without inserting a neutral frame.
- Live QA found a large SN:R hit -> rebound pose/camera jump in `sn_r_rebound.png`.
- Runtime fix: SN:R keeps `sn_r_hit` during its very short rebound phase while DOM `phase=rebound` remains correct; the discontinuous rebound PNG is retained for history but marked not used at runtime.
- Final QA run 35304314820: 216 live screenshots + DOM evidence, 0 browser errors, 0 asset/init warnings, stable character/drum registration on both viewports.
- `CHARACTER_QA_ISSUES.json`: all current measures 1-4 issues DONE; all 10 reviewQueue entries DONE.

## 2026-09-18
- Added a persistent character visual-QA/correction ledger and workflow for Luna Say Maybe M1-4, including status/timestamp/history rules and mandatory handoff links from WORK_SYNC and VARIANT_STATUS. Current full-resolution independent visual review is tracked explicitly rather than inferred from runtime validation.
- Revalidated the complete Luna Say Maybe measures 1-4 10-frame character set already imported through Dropbox staging; runtime key/phase mappings match SN:L, SN:R, HH:R, BD:RF, and BD+RC:* hit/rebound pairs. No neutral or drum_base changes were made in this verification pass.
- Replaced the final approved M1-4 character pose variants from Dropbox (hh_r_hit, hh_r_rebound, bd_rf_rebound, sn_r_rebound, bd_rc_rebound), preserving the approved upper-body direction while using the final natural lower-body mechanics; updated manifests/inventory/staging and bumped the character asset cache version.
- Replaced both fixed runtime layers from the two current-chat PNGs without regeneration: neutral SHA-256 `886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`, drum SHA-256 `dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85` (both 1448x1086 RGBA).
- Kept source-canvas registration at x=0/y=0; verified the character is centered over the kit with left foot at the hi-hat pedal region and right foot at the bass-drum pedal region.
- Set the character/drum backdrop to full opacity, preserved drum-behind/character-front z-order, and bumped `ASSET_VERSION` plus page cache keys to `20260918-neutral-drum-final-r1`.
- Replaced the fixed drum layer with the user-approved `/mnt/data/5215.png` source after verifying source SHA-256 `6d23c74667f453162bcb508cec56bfe82a5a9804eba210a3c0e6a4670dd03c30`.
- Preserved the approved drawing and converted only the white background to transparency for runtime use; imported PNG SHA-256 is `ad09946851e4184e466fb065c7491926a8bd8043bfd48f100b188af1c646f8a6`.
- Imported the runtime PNG from Dropbox to `character-assets/layers/drum/drum_base.png`; updated staging, manifest and Luna prototype inventory hashes.
- Pedal interpretation for this approved drum: left = hi-hat pedal, center = bass drum pedal, not a twin-pedal setup.
- Registered the current-chat attached character image as the fixed initial neutral/home ready pose. Original SHA-256: `46656f886ac7d7294f3b876aa55a38c1f7e8446834fd08cdccb2fa02b16b5b34`; transparent runtime SHA-256: `644ccf0a112b26087f401fb060f8855035b53a18a37f6a0a4500542b22bb8e81`.
- Imported the approved neutral through Dropbox staging to `character-assets/layers/character/base/neutral.png`, locked `lockedNeutralSha256`, and bumped the runtime asset cache version.

## 2026-09-17
- Reset Luna Say Maybe visual work back to measures 1-4 as the active refreshed prototype scope.
- Reconciled the temporary 1-16 runtime mismatch by restoring `site/character-prototype.js` to measures 1-4 in commit `d8f621ec57ee00372aa9c987f0782b6e7a7065ea`.
- Confirmed `asset_inventory.json` remains measures 1-4 with 28 notes / 27 time groups and action keys `SN:L`, `SN:R`, `HH:R`, `BD:RF`, `BD+RC:*`.
- Corrected project/status documentation to match the actual GitHub tree: neutral plus the 10 first-four-measure hit/rebound character variants are currently present.
- Added/updated `CURRENT_HANDOFF_CHAT_TO_WORK_2026-09-17.md` as the authoritative recovery point for both Normal Chat and Work.
- The user-approved replacement fixed drum PNG is still pending binary transfer. Expected SHA-256: `afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`. Manifest drum hashes must not change until that exact binary is committed.

## Historical entries
See Git history for earlier character-pose experiments and full-song / 1-16 / 1-8 milestones.
- 2026-09-18: M9-16 RC+SN:R/L hit retry rejected and deny-listed (`49a78e87...`): image generation returned `edit_op=null` and a fresh front-facing redraw instead of an approved-neutral-derived edit. Runtime scope remains 1-8; rebound/formal mapping/deploy remain blocked.

- 2026-09-18: User-approved `RC+SN:R/L` hit formally saved to Dropbox and GitHub as `combo/rc_sn_hit_refresh.png` (SHA-256 `f85cb4428d653b496938e50bbc486a2ddcab2a6d388884725946ba6d64e86a82`). Exact-key hit mapping is preloaded outside live scope; M9-16 remains blocked only on rebound and downstream QA.

## 2026-09-20 — Numeric RepairSpec V1
- Rewrote all active motion-defect repair specs as machine-readable numeric contracts.
- Added explicit zero-drift constraints, ROI/lock/anchor/contact/bbox/timing/validation fields and NEEDS_MEASUREMENT handling.
- Added REPAIR_SPEC_SCHEMA_V1.json and REPAIR_MEASUREMENT_RULES.md.
- Formal character PNGs were not modified.

- 2026-09-21 DMR-009 hit: created neutral-locked skeleton candidate from audited source-pixel HH/BD donors; fixed HH target (190,390), fixed-drum composite and transition QA recorded. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: created neutral-locked skeleton candidate from audited source-pixel HH/BD donors; fixed HH target (190,390), fixed-drum composite and transition QA recorded. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit continuation: repaired residual literal `\\n` tokens that kept the naturalized fast-path builder from executing, then re-requested the same one-image-only DMR-009 hit run with verified inputs reused. No rebound or second image was modified; formal promotion remains blocked pending regenerated QA.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.

- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.
