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

## Current highest-priority engineering goal
Improve drum-note timing extraction/synchronization against the original audio.

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
