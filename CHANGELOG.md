# Changelog

## 2026-09-18
- Replaced both fixed runtime layers from the two current-chat PNGs without regeneration: neutral SHA-256 `886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`, drum SHA-256 `dadc9764acebc0fc3db3c661ffa0929fb6a3c4cc7b03b27e10920ce796efed85` (both 1448x1086 RGBA).
- Kept source-canvas registration at x=0/y=0; verified the character is centered over the kit with left foot at the hi-hat pedal region and right foot at the bass-drum pedal region.
- Set the character/drum backdrop to full opacity, preserved drum-behind/character-front z-order, and bumped `ASSET_VERSION` plus page cache keys to `20260918-neutral-drum-final-r1`.
- Replaced the fixed drum layer with the user-approved `/mnt/data/5215.png` source after verifying source SHA-256 `6d23c74667f453162bcb508cec56bfe82a5a9804eba210a3c0e6a4670dd03c30`.
- Preserved the approved drawing and converted only the white background to transparency for runtime use; imported PNG SHA-256 is `ad09946851e4184e466fb065c7491926a8bd8043bfd48f100b188af1c646f8a6`.
- Imported the runtime PNG from Dropbox to `character-assets/layers/drum/drum_base.png`; updated staging, manifest and Luna prototype inventory hashes.
- Pedal interpretation for this approved drum: left = hi-hat pedal, center = bass drum pedal, not a twin-pedal setup.
- Registered the current-chat attached character image as the fixed initial neutral/home ready pose. Original SHA-256: `46656f886ac7d7294f3b876aa55a38c1f7e8446834fd08cdccb2fa02b16b5b34`; transparent runtime SHA-256: `644ccf0a112b26087f401fb060f8855035b53a18a37f6a0a4500542b22bb8e81`.
- Imported the approved neutral through Dropbox staging to `character-assets/layers/character/base/neutral.png`, locked `lockedNeutralSha256`, and bumped the runtime asset cache version.

## 2026-09-17
- Reset Luna Say Maybe visual work back to measures 1-4 as the active refreshed prototype scope.
- Reconciled the temporary 1-16 runtime mismatch by restoring `site/character-prototype.js` to measures 1-4 in commit `d8f621ec57ee00372aa9c987f0782b6e7a7065ea`.
- Confirmed `asset_inventory.json` remains measures 1-4 with 28 notes / 27 time groups and action keys `SN:L`, `SN:R`, `HH:R`, `BD:RF`, `BD+RC:*`.
- Corrected project/status documentation to match the actual GitHub tree: neutral plus the 10 first-four-measure hit/rebound character variants are currently present.
- Added/updated `CURRENT_HANDOFF_CHAT_TO_WORK_2026-09-17.md` as the authoritative recovery point for both Normal Chat and Work.
- The user-approved replacement fixed drum PNG is still pending binary transfer. Expected SHA-256: `afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`. Manifest drum hashes must not change until that exact binary is committed.

## Historical entries
See Git history for earlier character-pose experiments and full-song / 1-16 / 1-8 milestones.