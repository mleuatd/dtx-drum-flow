DTX Drum Flow の Luna Say Maybe 作業を、最新GitHub mainを唯一の正本として継続してください。

対象GitHub:
`mleuatd/dtx-drum-flow`

ブランチ:
`main`

最初に必ず以下を順に読んでください。
1. `character-assets/prototypes/luna_say_maybe_16m/CURRENT_PROJECT_STATE.json`
2. `character-assets/prototypes/luna_say_maybe_16m/M5_PLUS_PROGRESS_LEDGER.json`
3. `character-assets/prototypes/luna_say_maybe_16m/NEXT_IMPLEMENTATION_HANDOFF.md`
4. `character-assets/prototypes/luna_say_maybe_16m/PRODUCTION_PIPELINE.md`

現在のlive runtimeScopeは 1〜8 です。
次のproduction queueは:
- ASSETQ-001
- actionKey: RC+SN:R/L
- phase: hit
- block: B09_16
- status: BLOCKED_IMAGE_GENERATION_REQUIRED
- reason: Immediate M9-16 blocker; corrected pair does not exist.

作業開始前に、CHARACTER_ASSET_GENERATION_SPEC.md / INSTRUMENT_CONTACT_POINTS.json / ASSET_NAMING_RULES.md / QA_CHECKLIST_MASTER.json / REJECTED_ASSET_REGISTRY.json を読んでください。

approved assetは再生成・上書きしないでください。
Rejected / NEVER_USE資産は絶対に再利用しないでください。
不足画像をneutralで代替してPASSにしないでください。
必要画像とQA gateが揃うまでruntimeScopeを拡張しないでください。

PRODUCTION_PIPELINE_SPEEDUP と NEXT_ASSET_QUEUE の最初の未完了項目から、自律的に処理してください。
画像生成が必要な項目だけBLOCKEDにし、画像生成なしでできる他作業は止めずに進めてください。
完了ごとに台帳を更新し、小さくcommit/pushしてください。

現時点のNEVER_USE registry件数: 11
現在の次推奨作業: Create corrected RC+SN:R/L hit/rebound from approved neutral; run NIMG-013..023; extend live runtime to 1-16 only after QA passes.
