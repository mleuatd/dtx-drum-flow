# Pipeline Usage Policy

Status: **CURRENT / MANDATORY**

For Luna Say Maybe implementation work, repository tools/workflows are the default execution path, not optional helpers.

## Mandatory startup
Read, in order:
1. CURRENT_PROJECT_STATE.json
2. M5_PLUS_PROGRESS_LEDGER.json
3. NEXT_IMPLEMENTATION_HANDOFF.md
4. PRODUCTION_PIPELINE.md
5. PIPELINE_USAGE_POLICY.json

Then run the production pipeline dispatcher for the task category.

## Pipeline-first rule
If a repository tool/workflow already performs an operation, use it rather than reproducing the same operation manually in chat/code.

Manual duplication is allowed only when the existing tool is unavailable, broken, or cannot cover the required case. In that event:
- record a `MANUAL_OVERRIDE` in the ledger,
- name the skipped tool,
- record why it could not be used,
- record evidence/output,
- add a follow-up task to repair/extend the tool if the operation is likely to recur.

## Self-improvement rule
If the same manual operation is encountered twice, it must be promoted to a reusable tool/workflow before a third repetition.

## Completion rule
A task is not considered pipeline-compliant merely because the final result is correct. Where a mandatory tool/workflow exists, either:
- its use is evidenced, or
- a MANUAL_OVERRIDE is recorded.

This policy does not force image generation. It governs planning, QA, staging, mapping, validation, handoff and repeatable production operations.
