# Changelog

## 2026-09-15
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
