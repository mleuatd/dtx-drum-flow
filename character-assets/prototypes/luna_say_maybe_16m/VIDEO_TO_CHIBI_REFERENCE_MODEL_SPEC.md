# VIDEO_TO_CHIBI_REFERENCE_MODEL_SPEC

Status: **CURRENT IMPLEMENTATION SPEC / HYBRID AI + DETERMINISTIC**  
Updated: 2026-09-19T19:35:00+09:00


## North-star goal

All video-derived appearance modeling, chibi retargeting, AI-assisted rendering, cowlick normalization, and line-style normalization exist only to support the final runtime deliverable:

**character frame assets for DTX Drum Flow that animate naturally behind the notes and appear to perform the drum chart correctly in the web runtime.**

The appearance model is not the final product by itself.

The final product is the runtime-ready character frame set mapped to actionKey / phase and validated against the fixed drum layer.

日本語要約：

**動画モデルそのものは成果物ではない。最終成果物は、DTX Drum Flow のWeb runtimeでLuna Say Maybeのノーツに合わせて自然にドラム演奏する4頭身人物コマ画像群である。**

Every infrastructure decision must be judged by whether it improves runtime frame quality, reproducibility, contact correctness, and scalable frame production.

## Purpose
Build a reusable numeric appearance/geometry reference from the user's 360-degree character video, then retarget that reference to the existing DTX Drum Flow four-head chibi character system without replacing the established drum-action logic.

The end goal is:

`360 video appearance -> multiview numeric reference -> 4-head chibi retarget -> existing DTX action pose -> constrained render -> cowlick normalization -> pencil-line normalization -> fixed-drum QA`

The source video defines **appearance and multiview shape information**. Existing DTX action assets/limb sidecars/fixed-drum contact data define **motion and instrument contact**.

## Reference video
- filename: `GAME_20260919-191516~3.mp4`
- SHA256: `33c0feabad6ea0cfa1c0752ed359f719b7c4443c540d01da633b964a036b0479`
- bytes: 13,219,147
- resolution: 564 x 1320
- frames: 2,448
- fps: ~58.8742
- duration: ~41.5802 seconds
- coverage: approximately one full 360-degree rotation

The source supplies front, quarter, side, rear-quarter and rear views and is suitable for multiview appearance calibration.

## Important limitation
A single monocular rotating video does not provide guaranteed metric 3D geometry. This subsystem stores a **multi-view normalized reference model** rather than claiming an exact reconstructed 3D mesh.

Optional AI/pose-estimation providers may estimate 2D/relative-3D landmarks, segmentation and silhouette anchors. Those estimates are observations with confidence values, not unrestricted rendering authority.

## Model separation

### Appearance model
Derived from the 360 reference video:
- long dark-teal hair family and back-hair mass,
- side locks and crown/cowlick relationship,
- long gray check jacket and hem/sleeve silhouette,
- dark inner top,
- dark short skirt,
- black ankle boots,
- angular silhouette observations by yaw,
- normalized landmark/garment anchors,
- relative lengths and widths.

### Motion model
Derived from existing DTX data:
- approved neutral,
- hit/rebound variants,
- authoritative limb sidecar,
- instrument contact points,
- fixed drum registration,
- transition rules.

Appearance must never overwrite motion semantics. Motion must never freely redesign the appearance.

## 4-head retarget rule
Runtime target is `headCount = 4.0`.

A pose observation stores at minimum head-top, chin, shoulders, elbows, wrists, hips, knees and ankles. Retargeting uses head length as the unit. The head is retained as the target unit and the body below the chin is compressed to reach four total head units while preserving joint order and left/right identity.

Horizontal proportions may use a profile scalar to preserve chibi readability. Instrument contact remains higher priority than cosmetic exactness.

## Multiview reference sampling
`tools/reference_model/extract_reference_views.py` samples representative views and writes frame index, timestamp, provisional yaw and SHA for each extracted image.

The first profile uses 12 samples across the full turn. Yaw is a normalized sequence coordinate and may later receive a calibrated zero-offset/direction. Do not claim world-space camera calibration from this alone.

## Landmark / silhouette observation schema
Each view may carry an observation sidecar with:
- pose joints: head_top, chin, neck, shoulders, elbows, wrists, hips, knees, ankles,
- hair anchors: crown, left/right side-lock extrema, back-hair width extrema, hair-tip center/left/right,
- garment anchors: jacket shoulder corners, lapel points, jacket hem corners, skirt hem corners,
- footwear anchors: ankle and toe/heel extrema,
- silhouette bbox,
- confidence per point,
- provider (`manual`, `AI`, `pose_model`, `segmentation_model`),
- source frame SHA.

AI may propose these values. A deterministic stage consumes them.

## AI-assisted mode
AI is permitted only to:
1. propose landmarks/silhouette/garment anchors from extracted reference frames,
2. fill missing multiview observations with confidence labels,
3. render a candidate from a numeric constraint package when deterministic raster compositing is insufficient.

AI is not allowed to freely choose character identity, outfit, hair family/length, head count, camera family, limb side, instrument target, or fixed-drum registration.

`tools/reference_model/build_render_constraint_package.py` exports the hard constraints that must accompany any AI-assisted render.

## Deterministic retarget tool
`tools/reference_model/retarget_chibi.py` transforms a numeric pose to the target head count without image generation. It outputs retargeted joint coordinates and carries appearance/render constraints forward.

## Render and post-processing pipeline
1. choose existing DTX action/phase and authoritative contact target,
2. obtain/construct numeric pose joints,
3. retarget to 4.0 head count,
4. combine with video-derived appearance constraints,
5. render deterministically where possible or AI-assisted under the exported constraint package,
6. apply `tools/cowlick/apply_cowlick.py` if required,
7. apply `tools/line_style/normalize_line_style.py`,
8. composite with fixed drum and run reach/contact/registration QA,
9. compare against runtime camera/identity rules,
10. only then promote.

## Source-of-truth priority
1. GitHub main current master rules
2. fixed drum + contact points + limb/action data for motion semantics
3. approved runtime camera/registration
4. this video-derived appearance model for outfit/hair/multiview shape
5. four-head retarget profile
6. AI suggestions only where not contradicted above

## Versioning
Video-derived models are immutable by profile id. A better extraction creates `v2`, not silent mutation of an approved `v1`.

## Acceptance gates
Infrastructure is ready when video metadata/SHA can be extracted, representative multiview frames can be deterministically sampled, a versioned appearance profile exists, retargeting to 4.0 heads runs from numeric joints, an AI constraint package can be emitted, and no formal PNG is overwritten.
