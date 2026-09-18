# Commit Boundary Rules

Status: CURRENT

Production work must be split so any bad step can be rolled back without losing previously approved evidence.

## Required boundaries
1. candidate / QA tooling or candidate metadata only
2. formal asset save only after static QA
3. manifest + ACTION_KEY_ASSET_MAP + inventory metadata
4. runtime mapping / runtimeScope changes
5. runtime QA evidence
6. documentation / ledger / handoff closure

## Rules
- Never combine first-time candidate creation with live runtimeScope expansion.
- Never combine rejected-candidate cleanup with approved-asset overwrite.
- Binary image bytes and mapping changes should be independently revertible.
- Every state transition must record commit SHA in the progress ledger/staging JSON.
- A runtimeScope commit is allowed only after all required assets for the contiguous target block are formally saved and statically approved.
- Documentation-only commits may follow code/data commits but must not falsely mark DONE before workflow evidence exists.
