# Asset Naming Rules

Status: CURRENT / REQUIRED FOR NEW ASSETS

## Canonical fields
Every new character asset is identified by:
- actionKey: limb-aware chart key, e.g. `BD+SN:RF/L`
- runtimeKey: wildcard combo runtime key where applicable, e.g. `BD+SN:*`
- phase: `hit` or `rebound`
- part tokens: alphabetical part order used by the full-song action inventory
- limb tokens: same order as part tokens
- lifecycle: formal / review / candidate / rejected
- revision marker: use `refresh` only when replacing an older drawing family while retaining semantic action

## Formal GitHub paths
Single part:
`character-assets/layers/character/<part>/<phase>_<limb-lower>[ _refresh].png`

Combo:
`character-assets/layers/character/combo/<parts-lower-underscore>_<phase>[ _refresh].png`

Examples:
- `SN:L` hit -> legacy compatible `sn/hit_l.png`
- `RD:R` hit refresh -> `rd/hit_r_refresh.png`
- `BD+SN:RF/L` hit refresh -> `combo/bd_sn_hit_refresh.png`
- future `HH+SN:R/L` hit -> `combo/hh_sn_hit.png`

Existing approved files are NEVER renamed merely to match this rule. New assets use this rule; ACTION_KEY_ASSET_MAP.json is the compatibility authority.

## assetKey
Canonical:
`<parts-lower-underscore>_<limbs-lower-underscore>_<phase>[_refresh]`

Examples:
- `sn_l_hit`
- `rd_r_hit_refresh`
- `bd_sn_rf_l_hit_refresh`

Runtime frame IDs may preserve existing legacy IDs for compatibility. New IDs should follow the canonical assetKey unless an existing convention requires a shorter stable ID.

## Dropbox
Formal approved transfer:
`/ChatGPT/dtx-drum-flow/<canonical-assetKey>_<YYYYMMDD>.png`

Candidate:
`.../<canonical-assetKey>_candidate_<YYYYMMDD>_<shortsha>.png`

Rejected:
Never rename a rejected file to resemble an approved file. Record its existing name/path/SHA in REJECTED_ASSET_REGISTRY.json.

## Combo ordering
Use the same alphabetical part order as FULL_SONG_ACTION_KEY_INVENTORY.json. Limb order follows part order. Never reorder by screen position.

## Versions
Do not append arbitrary v2/v3 to formal paths. Preserve revisions in Git history and SHA256. Use `refresh` only for the established refreshed drawing family. Candidate filenames may include short SHA.

## Lifecycle
- candidate/review: never runtime mapped
- formal: may be entered into manifest only after static QA
- runtime-ready: only after mapping/transition QA
- rejected: NEVER_USE

## Compatibility
Legacy current formal paths remain valid:
- SN/L/R, HH:R, BD:RF, BD+RC, RD:R refresh, BD+SN refresh.
The mapping master is the only supported bridge between canonical action keys and legacy filenames.
