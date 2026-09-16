# Character Variant Status

Last updated: 2026-09-16

Legend: TODO / DRAFT / APPROVED / COMMITTED

## Architecture

- [x] GitHub repository is source of truth
- [x] Layer separation rules committed
- [x] Fixed canvas: 1448x1086
- [x] Global registration fixed at x=0,y=0
- [x] Drum and character layers defined separately
- [x] Effect layer defined separately
- [x] Animation rule JSON committed
- [x] Score-binding JSON committed
- [x] Automatic quarter/eighth/sixteenth rule structure committed
- [x] Sixteenth alternating-hand rule committed
- [x] Simultaneous-hit mapping structure committed
- [x] Layer compositor committed
- [x] Asset validator committed
- [x] CI validation workflow committed

## Baseline binary assets

- [x] Baseline composition approved by user
- [x] Fixed camera / composition / style rules defined
- [x] Drum layer generated and SHA-256 identity registered in `baseline_reference.json`
- [x] Commit transparent fixed drum PNG bytes: `layers/drum/drum_base.png`
- [x] Character layer generated and SHA-256 identity registered in `baseline_reference.json`
- [x] Commit neutral transparent character PNG bytes: `layers/character/base/neutral.png`
- [x] Register all committed PNG dimensions, alpha requirement, status, use, and SHA-256 in `config/assets_manifest.json`
- [x] Lock `drum_base.png` SHA-256 in CI validation

Important: a raster baseline cannot be safely auto-separated into drum/person without a reviewed mask because their linework overlaps. Do not invent or shift pixels just to mark this complete.

## HH

| Asset | Status |
|---|---|
| prep_r | DRAFT |
| hit_r | COMMITTED |
| rebound_r | DRAFT |
| prep_l | TODO |
| hit_l | TODO |
| rebound_l | TODO |
| quarter mapping | COMMITTED |
| eighth mapping | COMMITTED |
| sixteenth R/L alternating mapping | COMMITTED |

Current HH preview work exists, but it is not authoritative until character-only transparent layers are extracted/approved against the locked drum layer.

## Other single-part variants

| Part | Hit | Rebound | 4th mapping | 8th mapping | 16th mapping |
|---|---|---|---|---|---|
| SN | COMMITTED | COMMITTED_DRAFT | COMMITTED | COMMITTED | COMMITTED |
| BD | COMMITTED | TODO | COMMITTED | COMMITTED | COMMITTED |
| HT | TODO | TODO | TODO | TODO | COMMITTED |
| LT | TODO | TODO | TODO | TODO | COMMITTED |
| FT | TODO | TODO | TODO | TODO | COMMITTED |
| LC | TODO | TODO | COMMITTED | TODO | TODO |
| RC | COMMITTED | TODO | COMMITTED | TODO | TODO |
| RD | COMMITTED | TODO | TODO | COMMITTED | TODO |

## Simultaneous-hit variants

| Combination | Rule | Image layer |
|---|---|---|
| SN + BD | COMMITTED | COMMITTED |
| HH + BD | COMMITTED | TODO |
| LC + SN | COMMITTED | TODO |
| RC + BD | COMMITTED | COMMITTED |
| Tom + Cymbal | COMMITTED | TODO |

## Working rule

Before creating or editing a pose:
1. read this file
2. read `LAYER_RULES.md`
3. keep the drum layer unchanged
4. create/edit character-only full-canvas transparent layer
5. validate
6. composite preview
7. obtain visual approval
8. mark APPROVED
9. commit binary layer and update this status

Do not regenerate APPROVED layers unless the user explicitly requests revision.

## Prototype scope

- [x] Luna Say Maybe measures 1-16 selected as the first prototype scope
- [x] First 16 measures extracted from FINAL notes chart
- [x] Per-note hand/foot animation metadata generated
- [x] Left-facing baseline orientation locked
- [x] Binary baseline layers transported into GitHub paths
- [x] Browser renderer wired to the prototype layer set
- [ ] Visual QA of all first-16-measure note patterns

## Luna 1-16 implementation

- [x] Runtime layer switcher implemented in `site/character-prototype.js`
- [x] Stage DOM/CSS layered backdrop implemented
- [x] Deploy workflow updated to publish `character-assets/` with the site
- [x] First-16 measure occurring pattern inventory committed
- [x] Generated local draft layers: neutral, HH right prep/hit/rebound, HH left hit, SN left hit, BD foot-down
- [x] Generate RC hit, RD hit, BD+SN, BD+RC, RC+SN combined poses
- [x] Commit PNG binary bytes for Luna 1-16 required generated layers
- [x] Verify all 144 notes / 124 simultaneous groups resolve to one of the nine required character frames
- [x] Make `asset_inventory.json` the browser runtime frame-map source
- [x] Align SN=left hand, BD=right foot, and combo names with the prototype files
- [ ] Add HH left-hand prep/hit/rebound frames for visually correct sixteenth-note HH alternation; the full-song runtime remains enabled using the safe right-hand/neutral fallback until those binaries are available

## Binary push transport

- [x] GitHub binary upload path validated with Git Data API
- [x] PNG bytes are uploaded as base64 blobs
- [x] Blobs are assembled into a tree, committed, and `main` is advanced with `update_ref`
- [x] Luna 1-16 required binary layers committed in commit `db3fdcd0b2038b5bb78f59d805472102fc621881`

## Current binary inventory

- GitHub `main`: 11 registered PNG files
- Fixed layer: 1 drum PNG (`APPROVED_LOCKED`)
- Character layers: neutral plus 8 required hit variants
- Visual state: neutral is approved; hit variants remain `COMMITTED_DRAFT` until individual visual review
- Machine-readable identities: `config/assets_manifest.json`
- Prototype mapping and per-frame identities: `prototypes/luna_say_maybe_16m/asset_inventory.json`

## First-four-measure runtime milestone

- [x] Measures 1-4 explicitly selected as the currently enabled browser range
- [x] 28 notes / 27 time groups verified
- [x] Required keys verified: `SN:L`, `BD:RF`, `HH:R`, `BD+RC:*`
- [x] All four required poses resolve to committed PNG files
- [x] Runtime preloads every used PNG before setting the character layer ready
- [x] Canvas lane background changed from opaque fill to translucent fill so the layers remain visible behind notes
- [x] CSS, app module, and character module URLs cache-busted together
- [x] Final public-page visual QA after deployment
- [x] Prep / hit / rebound phase switching implemented for all four occurring keys
- [x] Transparent SN left-hand rebound frame added and SHA-registered
- [x] Separate instrument-positioned comic hit-effect layer added
- [x] BD+RC simultaneous hits emit two independent effect bursts

Motion QA policy:
- SN uses a dedicated rebound drawing; HH, BD, and BD+RC currently return to the approved neutral pose for rebound.
- Six attempted HH/BD/BD+RC rebound generations were rejected before Git registration because the output was RGB with a baked checkerboard instead of real transparency.
- The runtime phase windows are prep before the note, hit at the note, and rebound after it. The nearest time group wins, which keeps the two closely spaced opening SN notes responsive without moving the drum layer.
- The effect is a separate SVG layer at the locked 1448x1086 coordinate system. It never changes drum pixels or character registration.

First-four-measure motion polish was deployed in commit `b96726f8cd4ab0b27b79b2ed06f8f4a330c6b0aa` and verified on GitHub Pages. Public-browser checks passed for SN hit/rebound and the two-position BD+RC effect. All four GitHub Actions runs completed successfully.

## Measures 5-8 runtime milestone

- [x] Measures 1-8 selected as the enabled browser range
- [x] Enabled range verified as 61 notes / 59 time groups
- [x] Measures 5-8 verified as 33 notes / 32 time groups
- [x] Measures 5-8 keys verified: `RD:R`, `SN:L`, `BD:RF`, `BD+RC:*`
- [x] Existing transparent RD right-hand image and RD effect coordinate wired into runtime phases
- [x] Every measures 5-8 hit resolves to the expected committed image
- [x] Every measures 5-8 non-rapid hit returns to neutral after 0.075 seconds
- [x] Same-key sixteenth-speed repeats retain rebound follow-through instead of resetting
- [x] No new PNG required; all necessary images were already registered

Measures 5-8 were deployed in commit `26adb1eabf70c14623a0a12ef4908f349af9eced`. GitHub Pages browser QA passed for RD hit, neutral settling, and the two-position BD+RC effect. All four GitHub Actions runs completed successfully.

Public QA result for commit `3d36aa5d148eebdbdb5fe4afc719c3c52115f543`:
- initial state: `character-ready active`, scope `1-4`, opacity `0.9`
- fixed drum and neutral character: loaded at 1448x1086
- canvas CSS background: transparent; JavaScript lane fill: translucent for Luna
- 5.0 seconds: switched to `layers/character/sn/hit_l.png`, pose `SN · L`
- 15.0 seconds: scope ended and the character backdrop became inactive
- `assets-missing`: false
- all four GitHub Actions: success
## Full-song runtime milestone

- [x] Luna Say Maybe measures 1-148 enabled from the FINAL chart
- [x] 2,158 notes / 1,527 simultaneous-time groups verified
- [x] All 23 occurring full-song group keys resolve to registered runtime frame/phase entries
- [x] HT / LT / FT hit-effect coordinates added
- [x] Three-position effect support added for triple simultaneous hits
- [x] Full-song validation uses the FINAL notes chart as source of truth
- [x] Unsupported combinations use documented closest-pose fallbacks instead of disabling animation
- [ ] Dedicated HT / LT / FT character hit/rebound PNGs (currently neutral character + correct instrument effect)
- [ ] Dedicated HH+BD / HH+SN / RD+SN / other later-song combo character PNGs
- [ ] HH left-hand transparent frames for visually correct R/L sixteenth alternation

Mechanical full-song verification: 1,527 / 1,527 groups resolved, 0 unresolved. 575 groups currently use fallback character poses; 100 tom-only groups use neutral character with instrument-positioned effects.


## 2026-09-17 measures 1-16 final QA pass

- Runtime scope restored and hard-limited to measures 1-16.
- Registered first-16 runtime PNGs passed structural checks: 1448x1086 and transparent PNG metadata present.
- COMMITTED_DRAFT hit variants remain visual-pending because this chat environment cannot expose GitHub PNG bytes to the visual/edit surface as an editable image target.
- `SN:R` remains the only exact-pose shortage in measures 1-16; neutral fallback is intentional and `SN:L` is not reused.
- No character PNG bytes were modified in this pass.
- No LT/FT or other measure 17+ variants were generated.
