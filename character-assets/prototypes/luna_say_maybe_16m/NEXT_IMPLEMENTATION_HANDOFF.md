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
