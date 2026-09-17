# Drum upload state

Always read this file before resuming the finalized drum upload.

- Repository: `mleuatd/dtx-drum-flow`
- Branch: `main`
- Target: `character-assets/layers/drum/drum_base.png`
- Final visual source: lossless, pixel-identical to the approved drum PNG
- Original PNG SHA-256: `afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`
- Optimized PNG SHA-256: `554c9817ddff8f296f3d278f999d359201c8d53980535021408cedf82cf2d8be`
- Transfer source format: lossless WebP, pixel-identical RGBA
- Transfer source bytes: `1281652`
- Transfer source SHA-256: `df2e3350fed53e66b6b804ab65c7b4393bf901af68fa55a35b8b53fb6141a36a`
- Pixel SHA-256 (raw RGBA): `e536b66a5a4afda4778b0801362526db30903f159057091106316c28abf8e0df`
- Safe chunk prefix: `tools/drum_asset/safe_webp_part_`
- Safe chunk count: `570` (`000` through `569`)
- Each full chunk file is about `3023` bytes. This size has been verified to survive the chat -> GitHub write path without truncation.

## Resume rule

1. Read this file first.
2. Ignore `final_part_*.json`, `stable_webp_part_*.json`, `part_*.json`, and `q_*.json`; they are abandoned probe/partial files and are NOT part of the final transfer.
3. Upload only `safe_webp_part_###.json` in small batches.
4. After each batch, verify each GitHub blob SHA against the locally prepared chunk, then update this file.
5. Do NOT create/update `tools/drum_asset/drum_base_manifest.json` until every safe chunk is present and verified; that manifest triggers the rebuild workflow.
6. After all 570 chunks are present, install/update the rebuild script if needed, then write the manifest last, let GitHub Actions reconstruct the WebP source, convert it back to PNG, verify raw RGBA pixel SHA-256, update metadata, and commit/push the final drum asset.

## Current progress

- Verified safe chunks: **000**
- Chunk 000 local/GitHub Git blob SHA: `209839a3be2854e9d3439077d4dfff2401f98d40`
- Next chunk: **safe_webp_part_001.json**
- Status: **READY TO RESUME**
