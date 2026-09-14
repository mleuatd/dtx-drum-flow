# Changelog

## 2026-09-15
- Established GitHub repository as the shared version-control location between ChatGPT Work and normal ChatGPT chats.
- Added shared project manifest and operating rules.
- Preserved the existing live site URL as the canonical deployment target.

- Reconstructed executable site source under `site/` from the current site's known behavior and requirements because the original ChatGPT Site projection source is not exportable from normal chat.
- Added browser-side MIDI / DTX / GDA parsing, internal drum playback, measure seeking, original-audio onset detection, and per-note timing realignment.
- Fixed initial JavaScript issues in DTX channel mapping and the note realignment loop.
