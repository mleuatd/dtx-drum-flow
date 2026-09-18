DTX Drum Flow の Luna Say Maybe 作業を、最新GitHub mainを唯一の正本として継続してください。

最初に必ず以下を順に読んでください。
1. `character-assets/prototypes/luna_say_maybe_16m/CURRENT_PROJECT_STATE.json`
2. `character-assets/prototypes/luna_say_maybe_16m/M5_PLUS_PROGRESS_LEDGER.json`
3. `character-assets/prototypes/luna_say_maybe_16m/NEXT_IMPLEMENTATION_HANDOFF.md`
4. `character-assets/prototypes/luna_say_maybe_16m/PRODUCTION_PIPELINE.md`
5. `character-assets/prototypes/luna_say_maybe_16m/PIPELINE_USAGE_POLICY.json`

最重要:
反復可能な作業を手作業で始める前に、必ず
`node tools/production-pipeline-dispatcher.mjs <task-category>`
または
`node tools/start-pipeline-task.mjs <task-category>`
を使い、返された既存tool/workflowを優先してください。

同等処理を既存toolがあるのに手作業で再実装しないでください。
既存toolを使えない場合だけ、M5_PLUS_PROGRESS_LEDGER.jsonへ MANUAL_OVERRIDE として、
- skipped tool
- reason
- evidence
- follow-up repair/extension
を記録してください。

現在のlive runtimeScope: 1〜8
次のproduction queue:
- ASSETQ-001
- actionKey: RC+SN:R/L
- phase: hit
- block: B09_16
- status: BLOCKED_IMAGE_GENERATION_REQUIRED

approved assetは再生成・上書きしないでください。
Rejected / NEVER_USE資産は絶対に再利用しないでください。
不足画像をneutralで代替してPASSにしないでください。
必要画像とQA gateが揃うまでruntimeScopeを拡張しないでください。

台帳の最初の未完了項目から自律的に処理し、完了ごとに小さくcommit/pushしてください。
