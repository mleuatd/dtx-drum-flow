# DRUM AUDIO FINAL LOCK — 2026-09-19

Status: COMPLETED / LOCKED

The current acoustic drum sound and mixer balance are the approved completion baseline.

## Final mixer defaults
- BD/LB 2.50
- SN 1.00
- SideStick 0.80
- HH Closed 0.20
- HH Open 0.15
- LP HH 1.00
- HT 1.00
- LT 1.00
- FT 1.05
- RD 0.15
- Ride Bell 0.15
- LC 0.15
- RC 0.15

## Lock rules
- Do not retune the completed sound automatically just because QA can suggest a different value.
- Smoothness/psychoacoustic QA remains active as a regression guard.
- The development mixer remains available but collapsed by default.
- "完成音量へ戻す" restores these locked values.
- The synthetic oscillator kick experiment is rejected; BD remains acoustic-sample based.
- BASELINE_R20.md remains the rollback reference for the completed acoustic engine.
