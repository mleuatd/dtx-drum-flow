# Cowlick Normalization Workspace — 2026-09-19

This directory is a **non-runtime editing workspace** for normalizing the character crown/cowlick while preserving the existing DTX Drum Flow character set.

## Safety boundary

- Existing runtime/formal character PNGs are **not edited merely by creating or updating this workspace**.
- The pre-edit state is pinned at commit `e80b32c8deee0d925df97dbbc882c73f3a201687`.
- Recovery branch: `snapshot/character-pre-cowlick-edit-20260919`.
- The original neutral baseline at that snapshot is:
  - `character-assets/layers/character/base/neutral.png`
  - SHA256 `886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9`

## Comparison rule

Every character variant must be reviewed as:

`locked neutral/original baseline -> that single variant`

Never normalize by comparing variant A -> variant B -> variant C. This prevents accumulated style drift.

## Intended workflow

1. Finalize the crown/cowlick on the baseline.
2. Lock the corrected baseline with an exact SHA.
3. For each existing variant, compare it directly against the locked corrected baseline.
4. Preserve motion-specific differences only.
5. Normalize identity/style/crown features toward the locked baseline.
6. Record each review and candidate here before promoting anything to formal/runtime paths.

## Important

This workspace is intentionally separated from the runtime asset folders. Candidate files and review records belong here until explicit QA/promotion.
