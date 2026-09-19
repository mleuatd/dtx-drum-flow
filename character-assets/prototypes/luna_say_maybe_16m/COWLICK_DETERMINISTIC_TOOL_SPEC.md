# COWLICK_DETERMINISTIC_TOOL_SPEC

Status: **CURRENT_MANDATORY / IMPLEMENTATION SPEC**  
Updated: 2026-09-19T19:00:00+09:00  
Scope: DTX Drum Flow / Luna Say Maybe character crown/cowlick normalization.

## 1. Purpose

This subsystem replaces free-form generative image editing for the crown/cowlick task with a **deterministic local raster operation**.

Given:
- an existing character PNG,
- a locked cowlick profile JSON,
- and the expected source SHA/size,

the tool adds only the approved cowlick strokes inside a small crown ROI and refuses to produce an accepted result if any pixel outside that ROI changes.

The tool does not redraw the character, does not synthesize a new pose, and does not invoke a generative model.

## 2. Authoritative visual source

The cowlick geometry is calibrated from the user-provided 360-degree reference video:

- source filename: `GAME_20260918-125902~2.mp4`
- observed size: 2,867,502 bytes
- SHA256: `2387e59543b938e8b60f0d734230968fe0999b55283a8834c8ee81e8b3bf707c`
- observed video: 636x290, ~57.46 fps, 1212 frames

The video is reference provenance only. It is not required during normal patch application after the profile is locked.

Representative observations from the 360-degree sequence:
- the crown feature is a pair of narrow arcing strands/loops emerging from nearby roots,
- the apparent shape changes with view angle but remains a two-strand structure,
- both strands reconnect visually into the hair mass,
- the result must not collapse into a simple V, U, single fork, or two arbitrary floating lines.

These observations specialize, but do not weaken, `IMAGE_EDIT_MASTER_RULE.md`.

## 3. Current target camera class

All current Luna Say Maybe character layers use the same three-quarter-back/over-shoulder family. The first deterministic profile is therefore:

`luna_3q_back_left_v1`

Additional camera classes may be added only as separate locked profiles. Do not mutate one profile to fit unrelated camera angles.

## 4. Safety model

The tool MUST:

1. read the source PNG bytes,
2. verify dimensions,
3. optionally verify exact expected source SHA256,
4. define one explicit crown ROI,
5. render only inside that ROI,
6. compare source/output pixels outside ROI,
7. fail if `outside_roi_changed_pixels != 0`,
8. emit a JSON QA report with source SHA, output SHA, ROI, changed-pixel counts and profile id.

No accepted output may be written over a formal asset automatically. Promotion remains a separate operation.

## 5. Geometry model

Cowlick strokes are defined as cubic Bezier paths in normalized ROI coordinates.

Each path contains:
- start point,
- control point 1,
- control point 2,
- end point.

The locked profile must contain exactly two semantic strands for the current design.

Required topology:
- close roots,
- two independent strands,
- narrow negative space between them,
- tips visually land back into the crown/hair region,
- no floating terminal tips,
- no single parent stroke splitting into two.

## 6. Line construction

The baseline style is not reproduced by a thick digital stroke.

The deterministic renderer uses:
- one fine base width,
- 3-4 or more repeated passes per visible strand,
- fixed small pixel offsets from the profile,
- slightly varied opacity/offset while remaining deterministic,
- no solid fill.

The offsets are data, not random generation. The same source/profile must yield the same output under the same Pillow version.

## 7. Allowed and forbidden regions

For 1448x1086 Luna assets, profile `luna_3q_back_left_v1` owns only the crown ROI defined in `tools/cowlick/profiles/luna_3q_back_left_v1.json`.

Outside that ROI, changes are forbidden for face, head direction/silhouette, long hair, clothing, arms/hands/sticks, torso, legs/boots, stool and canvas registration.

## 8. CLI contract

```bash
python tools/cowlick/apply_cowlick.py \
  --input character-assets/layers/character/base/neutral.png \
  --profile tools/cowlick/profiles/luna_3q_back_left_v1.json \
  --output /tmp/neutral_cowlick_candidate.png \
  --qa-report /tmp/neutral_cowlick_candidate.qa.json \
  --expected-source-sha256 886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9
```

The command MUST exit nonzero on wrong dimensions, source SHA mismatch, invalid profile, outside-ROI mutation, or unsafe source overwrite.

## 9. Promotion workflow

Normal operation:

`formal source -> deterministic candidate -> QA report -> visual review -> formal promotion`

Never:

`text prompt -> whole new character -> formal promotion`

The first approved neutral result becomes the locked cowlick baseline. Variant propagation then applies the same locked profile independently to each formal variant from its own original bytes.

## 10. Variant propagation

Each source is independent:

`locked profile + formal variant N -> candidate N`

Never chain candidate N into candidate N+1.

Each result requires source SHA, output SHA, `outsideRoiChangedPixels = 0`, and candidate status separate from formal status.

## 11. Video calibration workflow

The profile-calibration workflow may use the 360-degree reference video to inspect representative frames. After geometry has been locked, normal execution does not require the video.

If a future profile revision is necessary:
1. preserve the previous profile file,
2. create a new profile id/version,
3. record reference-video SHA and selected frame indices,
4. compare old/new profile output before promotion.

## 12. Non-goals

This tool does not redraw limbs, repair drum contact, perform pose generation, infer arbitrary hair styles, replace the approved neutral, alter the fixed drum layer, or perform generative AI image editing.

## 13. Initial implementation acceptance criteria

The tool is accepted when:
- it runs on the approved neutral PNG,
- emits PNG + QA JSON,
- output remains 1448x1086,
- outside-ROI changed pixels are exactly 0,
- source remains unchanged,
- repeated runs are deterministic,
- automated tests verify SHA guard and outside-ROI guard.
