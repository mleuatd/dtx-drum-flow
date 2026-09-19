# Drum reliability QA ledger

Baseline audio: r21 completed sound. Do not retune timbre/volume while investigating delivery reliability.

| ID | Status | Finding | Action |
|---|---|---|---|
| DR-AUD-LOAD-001 | OPEN | Playback can begin before the asynchronous full acoustic preload has completed. On a cold/slow network, a requested sample can be absent at trigger time; the engine then loads it asynchronously and only plays it if it is not more than 30 ms late. This can present as an occasional missing hit. | Reproduce under intentionally delayed sample delivery, then gate playback or guarantee required buffers before scheduling. |
| DR-AUD-SPEED-001 | PASS | Warm/preloaded dense scheduling from 0.5x through 2.0x did not drop immediate triggers in browser QA. | Keep regression test. |
| DR-AUD-DENSE-001 | PASS | Existing overlap/runtime stress tests pass on CI. | Continue repeated stress loops. |

Rule: every confirmed defect is recorded here before correction, then changed to FIXED only after the reproducer and regression tests pass.
