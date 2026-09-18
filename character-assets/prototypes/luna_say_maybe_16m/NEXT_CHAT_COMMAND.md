DTX Drum Flow の Luna Say Maybe 作業を最新GitHub mainから継続してください。

最初に以下を読んでください。
1. `character-assets/prototypes/luna_say_maybe_16m/CURRENT_PROJECT_STATE.json`
2. `character-assets/prototypes/luna_say_maybe_16m/M5_PLUS_PROGRESS_LEDGER.json`
3. `character-assets/prototypes/luna_say_maybe_16m/OPEN_WORK_QUEUE.json`
4. `character-assets/prototypes/luna_say_maybe_16m/NEXT_IMPLEMENTATION_HANDOFF.md`
5. `character-assets/prototypes/luna_say_maybe_16m/PRODUCTION_PIPELINE.md`
6. `character-assets/prototypes/luna_say_maybe_16m/PIPELINE_USAGE_POLICY.json`

現在、画像生成なしで実行可能だった台帳残作業はすべて消化済みです。
live runtimeScopeは1〜8のままです。
既存BD+SN:RF/Lは exact runtime mapping まで先行登録済みで、live transition QAだけ未完了です。

次の唯一の実行可能化条件は、approved neutral/home pose PNGをこのチャットに画像として添付することです。
添付後は、
- ASSETQ-001 RC+SN:R/L hit
- ASSETQ-002 rebound
の順に進めてください。

hit指示:
`character-assets/prototypes/luna_say_maybe_16m/GENERATED_PROMPT_rc_sn_r_l_hit.md`

rebound指示:
`character-assets/prototypes/luna_say_maybe_16m/REBOUND_INSTRUCTION_rc_sn_r_l.md`

画像生成後は candidate QA → fixed-drum composite/contact QA → staging → formal save → NIMG-013..023 の順で、既存pipeline/toolを優先して自律的に進めてください。

Rejected/Never Use資産の再利用、neutral代替PASS、runtimeScopeの先行拡張は禁止です。


### Current blocker update
Latest RC+SN hit retry SHA256 `49a78e87adf12e88288a350f23d3081a7ac552cde4b1e8a66305fcc804d39d6c` is `NEVER_USE` because generation metadata reported `edit_op=null` and visual QA confirmed a fresh front-facing redraw. Retry only from the approved neutral as a true image edit; rebound remains blocked until hit passes.
