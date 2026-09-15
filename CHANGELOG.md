# Changelog

## 2026-09-15
- Completed a UI requirements sweep against prior user instructions.
- Added separate visible ON/OFF controls for generated drum audio and original-song audio.
- Split note-scroll speed from music playback speed; note speed now supports 0.5x to 8.0x in 0.1x steps.
- Notes now disappear at the judgment line instead of flowing past it, and the judgment line flashes on hit timing.
- Added automated UI contract checks covering the known mobile/Xperia controls and legacy interaction requirements.

- Established GitHub repository as the shared version-control location between ChatGPT Work and normal ChatGPT chats.
- Added shared project manifest and operating rules.
- Preserved the existing live site URL as the canonical deployment target.

- Reconstructed executable site source under `site/` from the current site's known behavior and requirements because the original ChatGPT Site projection source is not exportable from normal chat.
- Added browser-side MIDI / DTX / GDA parsing, internal drum playback, measure seeking, original-audio onset detection, and per-note timing realignment.
- Fixed initial JavaScript issues in DTX channel mapping and the note realignment loop.

- Added a precision audio-analysis pipeline under `tools/audio_pipeline/`.
- Added optional Demucs -> drumsep separation, optional ADTOF Plus transcription, original-mix transient reference, cross-source voting, confidence scoring, global timing-offset correction, local transient snapping, JSON/MIDI diagnostics, Windows helper scripts, and CI validation.
- Added browser import support for precision-pipeline `notes.json`.

- Completed the browser trainer baseline with drag-and-drop import, four-measure seek buttons, double-tap/double-click measure seeking, lane part icons, chart JSON export, original-audio playback, Web Audio scheduled drum hits, timing realignment, and precision-pipeline JSON import.
- Added GitHub Pages deployment workflow and deployment handoff documentation for eventual republishing to the existing ChatGPT Site URL.

- Recovered the actual Luna say maybe source MP3 and the previously generated drums-only MP3/MIDI from Library and performed real-audio validation.
- Measured per-family timing against original-mix frequency-band transient evidence. Kick aligned strongly; snare/toms/hihat/cymbals showed substantial low-confidence/likely misclassification regions.
- Added `validation/luna_say_maybe/REPORT.md` and diagnostics.
- Added `realign_existing_midi.py` for per-family global offset correction and local source-audio transient snapping.
- Updated the main pipeline to use frequency-band evidence and to degrade gracefully when Demucs/drumsep executables exist but required model weights are unavailable.
- Browser JSON import now preserves detailed drum-part labels and visualizes per-note confidence.

- Rebuilt Luna Say Maybe from the Songsterr reference drum chart (song 1089457, revision 3745733) instead of relying on audio-to-MIDI inference.
- Reconstructed 2,158 drum notes across 150 measures at BPM 139, including tuplets, and aligned the complete chart to the original instrumental audio with a +1.693 s global offset.
- Segment alignment checks ranged from +1.687 s to +1.699 s (12 ms total range), supporting a stable whole-song offset rather than per-note warping.
- Added Songsterr fetch and conversion tooling; final DTX/MIDI/notes JSON are stored in the shared Library, not the public repository.
- Fixed Songsterr MIDI export so simultaneous drum hits remain simultaneous.
