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