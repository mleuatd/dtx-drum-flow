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
- [x] Drum layer generated and SHA-256 identity registered in `baseline_reference.json`\n- [ ] Commit transparent fixed drum PNG bytes: `layers/drum/drum_base.png`
- [x] Character layer generated and SHA-256 identity registered in `baseline_reference.json`\n- [ ] Commit neutral transparent character PNG bytes: `layers/character/base/neutral.png`

Important: a raster baseline cannot be safely auto-separated into drum/person without a reviewed mask because their linework overlaps. Do not invent or shift pixels just to mark this complete.

## HH

| Asset | Status |
|---|---|
| prep_r | DRAFT |
| hit_r | DRAFT |
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
| SN | TODO | TODO | COMMITTED | COMMITTED | COMMITTED |
| BD | TODO | TODO | COMMITTED | COMMITTED | COMMITTED |
| HT | TODO | TODO | TODO | TODO | COMMITTED |
| LT | TODO | TODO | TODO | TODO | COMMITTED |
| FT | TODO | TODO | TODO | TODO | COMMITTED |
| LC | TODO | TODO | COMMITTED | TODO | TODO |
| RC | TODO | TODO | COMMITTED | TODO | TODO |
| RD | TODO | TODO | TODO | COMMITTED | TODO |

## Simultaneous-hit variants

| Combination | Rule | Image layer |
|---|---|---|
| SN + BD | COMMITTED | TODO |
| HH + BD | COMMITTED | TODO |
| LC + SN | COMMITTED | TODO |
| RC + BD | COMMITTED | TODO |
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
- [ ] Binary baseline layers transported into GitHub paths
- [ ] Browser renderer wired to the prototype layer set
- [ ] Visual QA of all first-16-measure note patterns
