# Drum reliability QA ledger

Baseline audio: r21 completed sound. Do not retune timbre/volume while investigating delivery reliability.

| ID | Status | Finding | Action |
|---|---|---|---|
| DR-AUD-LOAD-001 | FIXED / PASS | Playback can begin before the asynchronous full acoustic preload has completed. On a cold/slow network, a requested sample can be absent at trigger time; the engine then loads it asynchronously and only plays it if it is not more than 30 ms late. This can present as an occasional missing hit. | Deterministic 180 ms/sample cold-network reproducer confirmed the risk. Playback initialization now awaits the shared full preload promise before scheduling. Cold-load reproducer identified the defect; preload gate applied; runtime, speed, seek-start, overlap, psychoacoustic and chaos regressions passed. |
| DR-AUD-SPEED-001 | PASS | Warm/preloaded dense scheduling from 0.5x through 2.0x did not drop immediate triggers in browser QA. | Keep regression test. |
| DR-AUD-DENSE-001 | PASS | Existing overlap/runtime stress tests pass on CI. | Continue repeated stress loops. |\n| DR-AUD-SEEK-001 | PASS | 204 seek-start cases / 4,896 triggers across 0–240 s and 0.5x–2.0x completed without detected delivery loss. | Keep regression test. |\n| DR-AUD-CHAOS-001 | PASS | Rapid stop/restart, suspend/resume and ultra-dense repeated bursts completed without detected trigger loss. | Keep regression test. |

Rule: every confirmed defect is recorded here before correction, then changed to FIXED only after the reproducer and regression tests pass.
