# Drum reliability QA ledger

Baseline audio: r21 completed sound. Do not retune timbre/volume while investigating delivery reliability.

| ID | Status | Finding | Action |
|---|---|---|---|
| DR-AUD-LOAD-001 | FIXED / VERIFYING | Playback can begin before the asynchronous full acoustic preload has completed. On a cold/slow network, a requested sample can be absent at trigger time; the engine then loads it asynchronously and only plays it if it is not more than 30 ms late. This can present as an occasional missing hit. | Deterministic 180 ms/sample cold-network reproducer confirmed the risk. Playback initialization now awaits the shared full preload promise before scheduling. Run cold-start and speed regressions before closing. |
| DR-AUD-SPEED-001 | PASS | Warm/preloaded dense scheduling from 0.5x through 2.0x did not drop immediate triggers in browser QA. | Keep regression test. |
| DR-AUD-DENSE-001 | PASS | Existing overlap/runtime stress tests pass on CI. | Continue repeated stress loops. |

Rule: every confirmed defect is recorded here before correction, then changed to FIXED only after the reproducer and regression tests pass.
