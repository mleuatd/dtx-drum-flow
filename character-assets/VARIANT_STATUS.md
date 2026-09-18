# Character Variant Status

## Persistent visual QA ledger — 2026-09-18

All current and future character-pose visual defects are tracked in:
- `prototypes/luna_say_maybe_16m/CHARACTER_QA_ISSUES.json`
- `prototypes/luna_say_maybe_16m/CHARACTER_QA_WORKFLOW.md`

Every new chat/session must read the ledger before editing character assets. Completed items remain in the ledger as `DONE`; unnecessary items become `WONT_FIX` with a reason. Do not treat an asset as visually approved merely because manifest/runtime validation passes.


## Authoritative state — 2026-09-18

Active prototype scope: **Luna Say Maybe measures 1-4**.

GitHub `main` currently contains the complete 1-4 runtime frame set referenced by the inventory:
- `layers/character/base/neutral.png`
- `layers/character/sn/hit_l.png`
- `layers/character/sn/rebound_l.png`
- `layers/character/sn/hit_r.png`
- `layers/character/sn/rebound_r.png`
- `layers/character/hh/hit_r.png`
- `layers/character/hh/rebound_r.png`
- `layers/character/bd/hit_rf.png`
- `layers/character/bd/rebound_rf.png`
- `layers/character/combo/bd_rc_hit.png`
- `layers/character/combo/bd_rc_rebound.png`

Runtime action keys:
- `SN:L`
- `SN:R`
- `HH:R`
- `BD:RF`
- `BD+RC:*`

Runtime scope is 28 notes / 27 groups. The temporary 1-16 runtime change was rolled back; `site/character-prototype.js` and `asset_inventory.json` are aligned on measures 1-4.

Limb data remains authoritative:
- `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json`
- `site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json`

## Fixed neutral and drum — 2026-09-18
The current-chat attached PNGs are the authoritative fixed layers and were imported byte-for-byte after PNG, canvas, alpha, and SHA verification.

Neutral runtime path: `layers/character/base/neutral.png`  
Neutral SHA-256: `886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`  
Semantic role: `initial-neutral-home-ready-pose`  
Status: `APPROVED_FIXED`

Drum runtime path: `layers/drum/drum_base.png`  
Drum SHA-256: `dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85`  
Status: `APPROVED_FIXED`

Both canvases are 1448x1086. The runtime stack is drum behind character, with matching canvas registration and no per-layer translation or independent scale.

## Later-measure assets
Additional historical 1-16 character PNGs may still exist in the repository tree, but they are outside the active refreshed 1-4 visual scope and must not be treated as newly approved for expansion without explicit review.


## Refreshed expansion status — 2026-09-18

Live runtime remains **measures 1-4**. Runtime scope is now read from `asset_inventory.json`, not a hardcoded JS measure end. Post-refactor public QA passed in Runtime Character QA run `35321917979` / artifact `10536838661`.

### Measures 5-8
Authoritative chart/limb coverage:
- 33 notes / 32 groups / missing limbs 0
- keys: `BD:RF`, `RD:R`, `SN:L`, `BD+RC:*`
- M1-4 reuse: BD, SN:L, BD+RC

Blocker:
- refreshed `RD:R hit`
- refreshed `RD:R rebound`

Historical RD was rejected. Current-chat RD attempts were also rejected:
- first pair targeted screen-left instead of fixed-drum RD on screen-right;
- explicit-reference retry produced a different front-facing character.

No rejected RD file is registered or runtime-mapped.

### Measures 9-16
Coverage:
- 83 notes / 65 groups / missing limbs 0
- additional keys: `RD:R`, `BD+SN:RF/L`, `RC+SN:L/R`

BD+SN:
- visual QA PASSED, runtime QA PENDING
- hit: `layers/character/combo/bd_sn_hit_refresh.png`
- rebound: `layers/character/combo/bd_sn_rebound_refresh.png`
- hit SHA-256 `b222db6a71a4c3870865617432e40bce78c4aeb63ba7d674a17db89356843466`
- rebound SHA-256 `872962116a5e751b0985c1baa181368dc209e2cbffdc95f995e1ec5fbabeefa0`
- manifest status: `VISUAL_QA_PASSED_RUNTIME_PENDING`
- visual QA: run `35321151121`, artifact `10537157014`
- deliberately absent from runtime maps until the block can be tested coherently.

RC+SN:
- current-chat generated pair rejected because right-crash motion targeted screen-left.
- refreshed hit/rebound still required.

RD remains the shared blocker inherited from M5-8.

### Measures 17-148
No authoritative per-note limb sidecar exists after measure 16.

Analysis-only files:
- `site/charts/luna_say_maybe/Luna_say_maybe_full_limbs_DRAFT_ANALYSIS.json`
  - resolved by existing formal rules: 1,819
  - unresolved: 195
  - rapid-SN notes: 179
  - same-limb simultaneous conflict groups: 8
- `prototypes/luna_say_maybe_16m/FULL_SONG_ACTION_KEY_INVENTORY_DRAFT.json`
  - 2,014 notes / 1,403 groups
  - part-combination inventory only; no limb guessing.

Do not promote these drafts to runtime authority until rapid-SN rules and the eight conflict groups are formally resolved and validated.

### Persistent progress / skip ledger
Use:
`prototypes/luna_say_maybe_16m/M5_PLUS_PROGRESS_LEDGER.json`

It includes rejected generation SHA/reasons, misleading Dropbox aliases that must never be used, candidate/formal layer preservation status, QA evidence, and exact next actions.


## M9-16 non-image preparation — 2026-09-18 18:45 JST
- Live runtime is **measures 1-8**, not 1-4.
- M5-8 is DONE. Approved RD:R refresh pair is reused for M9-16; do not regenerate.
- BD+SN refreshed hit/rebound are formal-layer-saved and static visual-QA-passed; runtime QA remains pending.
- Corrected RC+SN hit/rebound is the only missing image pair blocking runtime expansion to M16.
- Authoritative RC+SN event: measure 13, time 25.649835, SN=L / RC=R. Runtime combo key will be `RC+SN:*`.
- Prepared expansion plan: `prototypes/luna_say_maybe_16m/M9_16_RUNTIME_EXPANSION_PLAN.json`.
- Target runtime scope after RC+SN approval: 1-16, 144 notes / 124 groups, expected keys `SN:L`, `SN:R`, `BD:RF`, `HH:R`, `BD+RC:*`, `RD:R`, `BD+SN:*`, `RC+SN:*`.
- Latest RC+SN regeneration attempt was rejected because it produced an unrelated front-facing redraw (`edit_op=null`). Image-generation rate limiting currently blocks retry; see `CHAR-QA-0007`.
