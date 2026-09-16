# Changelog

## 2026-09-16
- Added `assets_manifest.json` with full-canvas registration, alpha, status, use, and SHA-256 records for all 10 committed character-animation PNGs.
- Strengthened character asset validation to reject missing/unregistered PNGs, size or registration drift, missing transparency, empty layers, SHA changes, locked drum changes, inventory mismatches, note-count drift, and unresolved prototype animation groups.
- Made the Luna 16-measure browser renderer load its frame map from `asset_inventory.json`, keeping runtime filenames and the shared inventory in sync.
- Corrected animation configuration to use left-hand snare, right-foot bass drum, canonical BD+SN / BD+RC / RC+SN combo keys, and the committed combo filenames.
- Confirmed every one of the 144 prototype notes (124 time groups) resolves to one of the nine required character frames.
- Implemented the Luna Say Maybe measures 1-16 character-animation prototype renderer. The site now has a fixed drum/person layer stack, switches character poses from chart time, and only enables the prototype for Luna Say Maybe.
- Added a first-16-measure asset inventory: the prototype uses only SN, BD, RC, HH, RD plus BD+SN, BD+RC, and RC+SN simultaneous groups across 144 notes.
- Updated Pages deployment to copy `character-assets/` into the deployed site artifact so committed animation layers are available at runtime.
- Added a fixed-registration layered character-animation architecture for DTX Drum Flow. Drum kit, character motion, and optional hit effects are now managed as separate full-canvas layers so the drum hardware cannot jitter between frames.
- Locked character asset canvas/registration to 1448x1086 at x=0,y=0; cropping, per-frame translation, scaling, and mirroring are forbidden by project rules.
- Added JSON animation mappings for quarter/eighth/sixteenth patterns, including default R/L alternation for repeated sixteenth-note hi-hat hits and mappings for SN/toms, kick pedal motion, and common simultaneous-hit combinations.
- Added optional per-note JSON score binding via an `animation` object, while retaining automatic mapping from part, timing/subdivision, and simultaneous-note grouping.
- Added `site/character-animation.js` runtime rule resolver, a Python layer compositor, an asset-registration validator, binary asset conventions, and GitHub Actions validation.
- Added explicit status tracking for layer extraction. The approved raster baseline still needs reviewed transparent drum/person separation before binary layers can be marked authoritative; this is intentionally not auto-faked because overlapping linework makes blind segmentation unsafe.
- Reordered the 11-lane drum display so BD is centered between SN and HT, while retaining LP/LB and all existing chart part identifiers for JSON/MIDI/DTX compatibility.
- Upgraded built-in browser drum synthesis with a compressor-backed layered kit: stronger kick attack/body, shell+snare-wire snare, clearly separated closed/open hi-hat, pitched toms, distinct ride, longer crash tails, and a dedicated wooden cross-stick sound for GM note 37 (including Luna say maybe 2nd A-melody).
- Bumped the app cache key so GitHub Pages/mobile browsers receive the updated player immediately.

## 2026-09-15
- Added 「一体いつから」 FINAL drum chart from Songsterr song 3705140 revision 4853202, drum track index 3: 1,828 notes across 181 measures at BPM 175.
- Added reproducible Songsterr source/build metadata, FINAL-chart validation, and a third mobile song-selection button. Original-audio millisecond alignment remains pending until the source audio is supplied.

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
