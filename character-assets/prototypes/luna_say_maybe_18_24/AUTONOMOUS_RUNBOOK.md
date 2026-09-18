# Luna Say Maybe M18-24 Autonomous Runbook

GitHub main is the only source of truth. Public runtime QA is mandatory before this range is DONE.

Use the shared procedure in `docs/PUBLIC_RUNTIME_QA.md`. For this range run measures 18-24 and require `BD+RD:RF/R`, `RD+SN:R/L`, `BD+HH:RF/R`, and `HH+SN:R/L`, plus representative reused actions selected by the runner. Do not mark DONE from static QA alone.

On workflow failure, inspect the run job/log and `runtime-qa.json`, record the concrete failure in `PROGRESS.json`, fix the cause, commit, and let the new commit run. Do not loop reruns of an unchanged failing commit.
