# Character production source checkpoint — 2026-09-24

## Verified source

- GitHub `main` at inspection: `7dbe7808`.
- Fixed drum: `character-assets/layers/drum/drum_base.png` (1448 × 1086 RGBA), SHA-256 `dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85`; byte-identical to the user's `drum_base (3).png` attachment.
- Motion and outfit reference: user attachment `GAME_20260923-230152(2).mp4`, 720 × 1560, 36.59 seconds, SHA-256 `3c7cb87c188951a4c6fcac44cd71d0b162e2dbb0a30b7bf6cbab10ae317eaacd`. The attachment is not copied into GitHub.
- Existing approved drawing reference: `character-assets/layers/character/hh/hit_r.png` and `hh/rebound_r.png`, per `HH_R_FORMAL_SET_20260923.json`.
- Contact point reference: `character-assets/prototypes/luna_say_maybe_16m/INSTRUMENT_CONTACT_POINTS.json`; points are approximate, so inspect a composite at full size for each actual contact.
- Work queue: `IMAGE_PROGRESS_LEDGER.json`; `HH:R + SN:L` is already in progress. Do not reset or duplicate it.

## Production requirements from this request

Create hit and rebound for each remaining note combination as independent 1448 × 1086 transparent PNGs containing only the girl, drumsticks and stool. Keep the stool fixed relative to the canvas and the drum PNG untouched. Match the approved monochrome, loose mechanical-pencil line work, with the video's long hair, checked coat, short dark skirt and ankle boots. Each hit must visually contact its intended instrument, and each rebound must read as the immediately following pose. Validate both layers over the fixed drum, their sequence, and runtime selection before recording VERIFIED. Commit and push at usable checkpoints so later sessions can resume from `main` and the ledger.

## Current status

Source identification completed. No new action pair has been drawn or approved in this checkpoint; `HH:R + SN:L` remains in progress. Runtime must not be marked complete on the strength of this document.
