# Acoustic drum audio baseline — r20

Locked: 2026-09-19

This file marks the user-approved rollback point before further psychoacoustic/smoothness QA work.

- Baseline engine commit: c4873b08e28b4b0945791bf8fe90935fda64891d
- Public build: 20260919-acoustic-r20
- Synthetic kick reinforcement: absent
- Preserve current mixer balance while QA evolves.
- Any experimental audio change must be independently revertible to this baseline.
- Do not silently change loudness defaults while investigating smoothness.

Rollback target file:
- site/live-drum-engine.js @ blob c4873b08e28b4b0945791bf8fe90935fda64891d

QA expected at this baseline:
- Live Drum Smoothness QA: PASS
- Drum Overlap Smoothness QA: PASS
- Drum Runtime Browser QA: PASS
