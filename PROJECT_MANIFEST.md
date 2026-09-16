# DTX Drum Flow — Shared Project Manifest

## Canonical site
- Name: DTX Drum Flow
- Live URL: https://dtx-drum-flow.mleuatd.chatgpt.site
- Project ID: appgprj_6aa76fd7a1e48191b27d3b4793a85e70
- Slug: dtx-drum-flow
- Known projection revision at handoff: 3
- Known source version at handoff: 2

## Canonical version-control location
- GitHub repository: https://github.com/mleuatd/dtx-drum-flow
- Default branch: main
- This repository is the canonical shared history for changes made from ChatGPT Work and normal ChatGPT chats.

## Operating rules
1. Keep the live URL unchanged unless the user explicitly asks otherwise.
2. Before a meaningful code change, inspect the current repository state.
3. Record every meaningful change in Git history with a clear commit message.
4. Do not overwrite unrelated behavior unless intentionally requested.
5. Prefer reversible, incremental changes.
6. If Work and normal chat diverge, reconcile against this repository and document the decision here.
7. Update CHANGELOG.md for user-visible or behavior-changing modifications.

## Character animation / fixed registration

Canonical character asset management:
- `character-assets/`
- fixed canvas: 1448x1086
- registration: x=0,y=0
- fixed drum layer + separate character pose layer + optional effect layer
- never regenerate/move the drum kit per animation frame
- quarter/eighth/sixteenth and simultaneous-hit mappings: `character-assets/config/animation_rules.json`
- optional score metadata binding: `character-assets/SCORE_BINDING.md`
- site-side resolver: `site/character-animation.js`
- registration validation: `tools/character_layers/validate_assets.py`

Approved raster baseline geometry is authoritative. Binary transparent drum/person layers must be visually reviewed before being marked authoritative.

## Current highest-priority engineering goal
Complete and visually review the Luna Say Maybe measures 1-16 layered character-animation prototype without changing the fixed drum geometry.

Current binary state:
- 11 PNG layers are committed to `main`.
- `character-assets/config/assets_manifest.json` stores dimensions, registration, use, status, and SHA-256.
- `drum_base.png` is SHA-locked by validation.
- all 144 notes in the prototype resolve to the nine required character frames.
- generated hit variants remain committed drafts until visual approval.
- Luna measures 1-8 are the enabled runtime milestone; measures 9-16 remain prepared data.

The longer-term audio goal remains to improve drum-note timing extraction/synchronization against the original audio.

Use multiple signals rather than trusting a single Audio-to-MIDI path:
- separated drum stem
- original-audio transient/onset detection
- beat/BPM grid
- frequency-band-specific evidence for kick/snare/hat/cymbals
- local rhythmic pattern consistency
- per-note local realignment to the most plausible transient
- confidence scoring and optional fallback when confidence is low

## UI/interaction requirements already known
- Drum part lanes/icons for LC / HH / SN / HT / LT / FT / RC / RD / LP / LB / BD
- Double-tap/double-click left side: seek backward by measures
- Double-tap/double-click right side: seek forward by measures
- MIDI / DTX / GDA import
- Internal drum sound playback
- Playback-speed controls
- Timeline seeking

## CHANGELOG pointer
See CHANGELOG.md.

## Precision audio pipeline
- Location: `tools/audio_pipeline/`
- Preferred high-accuracy route: full mix -> Demucs drums stem -> drumsep per-kit stems -> per-stem onset detection -> optional ADTOF Plus MIDI -> global source-offset estimation -> multi-source consensus -> original-mix transient snap -> final JSON/MIDI.
- Browser integration: `site/parsers.js` accepts the generated `notes.json`.
- Heavy analysis is intentionally kept outside the browser.
- Third-party code and model weights are not vendored; upstream licenses apply.
