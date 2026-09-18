# Luna Say Maybe — Next Implementation Handoff

Updated: 2026-09-18 19:40 JST

## Read first
1. `CURRENT_PROJECT_STATE.json`
2. `M5_PLUS_PROGRESS_LEDGER.json`
3. latest GitHub `main`

Do not treat older contradictory text as current authority.

## Current live runtime
- Measures 1-8 only.
- Measures 1-4 DONE.
- Measures 5-8 DONE.
- Measures 9-16 are blocked only by the corrected `RC+SN:R/L` hit/rebound pair.

## Immediate next implementation block
`B09_16` — measures 9-16.

Why:
- public runtime expansion is contiguous;
- existing RD:R is approved;
- existing BD+SN:RF/L refresh pair exists and passed static/core QA;
- only corrected RC+SN:R/L hit/rebound are missing.

## Exact next work
1. Create corrected RC+SN:R/L hit/rebound from the approved neutral baseline.
2. Target screen-right RC with R hand and SN with L hand.
3. Reject any wrong-side, different-character, front-facing, drum-leaking or non-edit result.
4. Run NIMG-013 through NIMG-023 in `M5_PLUS_PROGRESS_LEDGER.json`.
5. Save approved RC+SN to Dropbox and GitHub formal refresh paths.
6. Update manifest/inventory mappings.
7. Extend live runtimeScope from 1-8 to 1-16 only after asset/static QA passes.
8. Run validation, Pages deploy, PC/Xperia live runtime QA and screenshot inspection.
9. Recheck the two previously blocked transitions:
   - BD+SN@25.434007 -> RC+SN@25.649835
   - RC+SN@25.649835 -> BD:RF@25.865662

## Reusable assets — do not regenerate
- SN:L
- SN:R
- HH:R
- BD:RF
- BD+RC:RF/R
- RD:R
- BD+SN:RF/L (runtime pending; do not redraw)

## Full-song planning authority
- `FULL_SONG_ACTION_KEY_INVENTORY.json`
- `FULL_SONG_ASSET_IMPLEMENTATION_PLAN.json`
- `FULL_SONG_IMPLEMENTATION_BLOCK_PLAN.json`
- `FULL_SONG_EXISTING_ASSET_QA_PLAN.json`

Full-song facts:
- 2,158 notes
- 1,527 time groups
- 30 limb-aware action keys
- REUSE_APPROVED 6
- REUSE_NEEDS_RUNTIME_QA 1
- NEW_IMAGE_REQUIRED 22
- BLOCKED 1
- 44 later new image files plus the 2 blocked RC+SN files

## Post-M16 planning
Formal public runtime must remain contiguous. After M9-16 is complete, M17 is the next live block even though it requires six new action-key pairs.

Low-novelty later blocks that are efficient for asset planning after dependencies clear:
- M18-19: 2 new pairs
- M20-24: 2 new pairs
- M105-108: 2 new pairs
- M109-129: 3 new pairs

Do not skip missing earlier measures when expanding public runtimeScope.

## Historical / never-use
Never use:
- rejected wrong-side RC+SN generations;
- rejected wrong-side/different-character RD generations;
- drum-leaking BD+SN first attempts;
- misleading Dropbox aliases documented in the ledger;
- historical draft limb/action inventory as current authority.

## QA
Reusable post-M16 QA schedule:
`FULL_SONG_EXISTING_ASSET_QA_PLAN.json`

It contains exact pre/hit/rebound/post sample times for 775 reusable-asset events on PC 1280x900 and Xperia 384x864.

## Autonomy rule
Do not ask the user about naming, file placement, block boundaries, QA timestamps, reuse classification, or validation fixes when current GitHub data already determines the answer.

## Implementation infrastructure — REQUIRED BEFORE FUTURE ASSET WORK
- Naming: `ASSET_NAMING_RULES.md/json`
- Action mapping: `ACTION_KEY_ASSET_MAP.json`
- Generation/edit spec: `CHARACTER_ASSET_GENERATION_SPEC.md`
- Instrument targets: `INSTRUMENT_CONTACT_POINTS.json`
- Motion rules: `POSE_TRANSITION_RULES.json`
- QA checklist: `QA_CHECKLIST_MASTER.json`
- Reject deny-list: `REJECTED_ASSET_REGISTRY.json`
- DONE gates: `BLOCK_COMPLETION_DEFINITION.json`
- One-command QA: `.github/workflows/luna-block-qa.yml` with `tools/luna-block-qa.mjs`

Runtime combo resolution is now exact limb-aware key first, legacy wildcard second. Existing M1-8 behavior is preserved. Before any new image generation/edit, read the generation spec, contact master, naming rules and QA checklist. Before runtime mapping, consult ACTION_KEY_ASSET_MAP and the rejected registry.


## Production Pipeline Speedup — COMPLETE

Read `PRODUCTION_PIPELINE.md` after CURRENT_PROJECT_STATE / ledger / this handoff.

Current production entrypoint:
- `NEXT_ASSET_QUEUE.json`
- next: ASSETQ-001 = corrected `RC+SN:R/L` hit
- then ASSETQ-002 = corrected rebound

Do not manually reconstruct production steps when a pipeline tool exists.
Use:
- prompt builder
- rebound derivation
- candidate QA/composite/diff
- staging JSON
- registration plan
- block checklist
- reuse finder
- risk-aware sampling
- QA summary
- Fast/Full Path workflows
- next-chat command generator

Risk-aware M1-8 regression after runner integration: run 35340512012 SUCCESS, artifact 10544374908.
Production pipeline contract validation: run 35340578530 SUCCESS.

## Mandatory pipeline-first execution
Before repeatable work, run `node tools/production-pipeline-dispatcher.mjs <task-category>` or `node tools/start-pipeline-task.mjs <task-category>`.
Use the returned existing tools/workflows instead of recreating equivalent logic manually.
If a required existing tool cannot be used, record a `MANUAL_OVERRIDE` with skipped tool, reason, evidence and follow-up repair/extension task.
A result can be technically correct but still non-compliant if a mandatory existing tool was skipped without override evidence.

## Open-work sweep — 2026-09-18 21:51 JST

All currently executable non-image ledger work has been exhausted.

- OPEN_WORK_QUEUE: `OPEN_WORK_QUEUE.json`
- total normalized work items: 19
- DONE now: 1 (approved BD+SN:RF/L exact runtime preload outside live scope)
- BLOCKED: 18
- canRunNow: 0
- live runtimeScope remains 1-8

Immediate blocker:
1. attach the approved neutral/home pose PNG as a usable image target in the current chat;
2. create `ASSETQ-001 RC+SN:R/L hit` using `GENERATED_PROMPT_rc_sn_r_l_hit.md`;
3. after visual acceptance, create `ASSETQ-002 rebound` using `REBOUND_INSTRUCTION_rc_sn_r_l.md`;
4. then continue NIMG-013 through NIMG-023.

Existing approved BD+SN:RF/L frames are now preloaded under exact runtime key `BD+SN:RF/L` while public/live runtimeScope remains 1-8. They are NOT yet live-transition-approved.

## RC+SN retry update — 2026-09-18 21:40 JST
- Approved neutral was located and previewed from Dropbox/GitHub, but the image generator did not bind it as a true edit source.
- Retry candidate SHA256 `49a78e87adf12e88288a350f23d3081a7ac552cde4b1e8a66305fcc804d39d6c` returned `edit_op=null` and a fresh front-facing redraw.
- Candidate is `NEVER_USE`; it was not registered, mapped, saved as formal, or deployed.
- `runtimeScope` remains 1-8.
- Next action: retry `ASSETQ-001` only with the approved neutral supplied as an actual image-edit target; do not create rebound until hit passes formal baseline-preservation QA.

## RC+SN hit implementation update — 2026-09-18 22:05 JST
- User approved the current RC+SN:R/L hit for implementation.
- Formal GitHub path: `character-assets/layers/character/combo/rc_sn_hit_refresh.png`
- Dropbox: `/ChatGPT/dtx-drum-flow/rc_sn_r_l_hit_refresh_20260918.png`
- SHA256: `f85cb4428d653b496938e50bbc486a2ddcab2a6d388884725946ba6d64e86a82`
- Binary import workflow run: `35347550282` SUCCESS; import commit: `127f430df5dbc118f42b8b09128b7cd2ff387074`.
- Exact runtime key hit preload: `RC+SN:R/L` -> `rc_sn_r_l_hit_refresh`.
- Live `runtimeScope` intentionally remains 1-8.
- Next image is only `ASSETQ-002`: create rebound from this accepted hit. Do not regenerate neutral or hit.
