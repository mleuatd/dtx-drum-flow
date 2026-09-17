# Drum upload state

Always read this file before resuming the finalized drum upload.

- Repository: `mleuatd/dtx-drum-flow`
- Branch: `main`
- Target: `character-assets/layers/drum/drum_base.png`
- Source: lossless-recompressed, pixel-identical finalized drum PNG
- Final source bytes: `2038286`
- Final source SHA-256: `554c9817ddff8f296f3d278f999d359201c8d53980535021408cedf82cf2d8be`
- Original user PNG SHA-256: `afb3eb8ac19039ffbe756691a54e4403b99dfd4d6c42a1a47e234b1eb9a09b6d`
- Chunk prefix: `tools/drum_asset/final_part_`
- Chunk count: `136` (`000` through `135`)
- Upload rule: commit chunks in small batches; update this file after each batch.
- IMPORTANT: do NOT create/update `tools/drum_asset/drum_base_manifest.json` until every final chunk is present. Updating that manifest triggers the rebuild workflow.
- Current completed range: **none yet**
- Next chunk: **final_part_000.json**
- After all chunks: upload `drum_base_manifest.json` from the local prepared set, wait for `Rebuild drum asset`, verify SHA-256 `554c9817ddff8f296f3d278f999d359201c8d53980535021408cedf82cf2d8be`, then verify the bot commit `assets: finalize corrected 11-lane drum layer`.
