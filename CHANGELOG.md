# Changelog

## 2026-09-18 — M5+ refreshed continuation / progress-ledger pass
- Added `M5_PLUS_PROGRESS_LEDGER.json` to track completed, in-progress, skipped/rejected, runtime-pending and unresolved work by measure block.
- Recorded every current-chat generation attempt with SHA/reason. Rejected: wrong-side RD pair, drum-leaking first BD+SN pair, wrong-side RC+SN pair, unrelated management-sheet misgeneration, and a later front-facing/different-character RD retry.
- Corrected BD+SN hit/rebound were preserved in Dropbox, imported review-only to GitHub, visually QA'd over the fixed drum (run `35321151121`, artifact `10537157014`), then copied to formal layer paths:
  - `character-assets/layers/character/combo/bd_sn_hit_refresh.png`
  - `character-assets/layers/character/combo/bd_sn_rebound_refresh.png`
  Both remain `VISUAL_QA_PASSED_RUNTIME_PENDING`; no runtime mapping yet.
- Added review-only candidate import workflow. Fixed missing Pillow and missing Dropbox secret by supporting per-asset short-lived download URLs. Candidate import succeeded in commit `36a4c7706f2110aa9040f3dedcdf1fff968af8b0`.
- Refactored `site/character-prototype.js` to read runtime measure scope from `asset_inventory.json` instead of hardcoding measure 4. Current inventory remains measures 1-4, so public behavior is unchanged.
- Updated UI contract test for inventory-driven scope and adjusted character asset validation to allow registered later-measure runtime-pending layers while separately enforcing the active M1-4 runtime set.
- Public GitHub Pages redeploy succeeded. Live Playwright runtime QA after the scope refactor succeeded: run `35321917979`, artifact `10536838661`.
- Added full-song limb analysis draft: 1,819 mechanically resolved notes, 195 unresolved notes, 179 rapid-SN notes, 8 same-limb simultaneous conflict groups. Draft remains analysis-only.
- Added later-measure part-combination inventory for measures 17-148: 2,014 notes / 1,403 groups, with no limb guessing.
- Current hard blocker for live expansion remains refreshed RD:R hit/rebound. RC+SN also still needs regeneration. Historical/rejected images are explicitly forbidden from reuse.

## 2026-09-18 — Refreshed Luna M5+ expansion preparation
- Started the requested refreshed expansion from measure 5 onward using completed M1-4 as the absolute visual baseline; the live runtime remains M1-4 until new frames pass QA.
- Recomputed measures 5-8 from FINAL notes + authoritative limb sidecar: 33 notes / 32 groups; only new action key is RD:R.
- GitHub Actions visual QA run 35315598184 / artifact 10535695236 compared the historical RD hit against the refreshed baseline. The historical frame was rejected for different line treatment, proportions, camera/body presentation and registration.
- Recomputed measures 9-16: 83 notes / 65 groups / missing limb assignments 0. New keys beyond approved M1-4 are RD:R, BD+SN:RF/L and RC+SN:L/R.
- GitHub Actions visual QA run 35315877548 / artifact 10535690785 rejected the historical BD+SN and RC+SN hit frames as incompatible with the refreshed baseline.
- Added M5-8 and M9-16 required-asset manifests. Refreshed measures 5-16 require six new direct-edit frames: RD hit/rebound, BD+SN hit/rebound, RC+SN hit/rebound.
- Verified the FINAL chart contains 2,014 notes after measure 16 through measure 148, with no embedded limb/hand/foot metadata. The only precomputed authoritative limb sidecar currently covers measures 1-16; measure 17+ mapping must not guess limbs.
- Added QA issues CHAR-QA-0005 and CHAR-QA-0006. Historical later-measure PNGs remain unapproved and are not wired into refreshed runtime.

## 2026-09-18 — M1-4 live runtime character QA closure
- Added/used Playwright GitHub Actions live-browser QA against the public GitHub Pages build at PC 1280x900 and Xperia-class portrait 384x864.
- Fixed rapid-hit phase timing so rebound can exist between closely spaced notes without inserting a neutral frame.
- Live QA found a large SN:R hit -> rebound pose/camera jump in `sn_r_rebound.png`.
- Runtime fix: SN:R keeps `sn_r_hit` during its very short rebound phase while DOM `phase=rebound` remains correct; the discontinuous rebound PNG is retained for history but marked not used at runtime.
- Final QA run 35304314820: 216 live screenshots + DOM evidence, 0 browser errors, 0 asset/init warnings, stable character/drum registration on both viewports.
- `CHARACTER_QA_ISSUES.json`: all current measures 1-4 issues DONE; all 10 reviewQueue entries DONE.

## 2026-09-18
- Added a persistent character visual-QA/correction ledger and workflow for Luna Say Maybe M1-4, including status/timestamp/history rules and mandatory handoff links from WORK_SYNC and VARIANT_STATUS. Current full-resolution independent visual review is tracked explicitly rather than inferred from runtime validation.
- Revalidated the complete Luna Say Maybe measures 1-4 10-frame character set already imported through Dropbox staging; runtime key/phase mappings match SN:L, SN:R, HH:R, BD:RF, and BD+RC:* hit/rebound pairs. No neutral or drum_base changes were made in this verification pass.
- Replaced the final approved M1-4 character pose variants from Dropbox (hh_r_hit, hh_r_rebound, bd_rf_rebound, sn_r_rebound, bd_rc_rebound), preserving the approved upper-body direction while using the final natural lower-body mechanics; updated manifests/inventory/staging and bumped the character asset cache version.
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