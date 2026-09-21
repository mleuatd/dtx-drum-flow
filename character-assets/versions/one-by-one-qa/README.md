# One-by-one image QA

This directory is the current-state authority for single-image repair experiments.

## Read order
1. `CURRENT_STATUS.json`
2. `REPAIR_PIPELINE_PATTERNS.json`
3. `STRIKE_CONTACT_QA_RULES.json`
4. case-specific previous QA / attempt JSON
5. fixed `POSE_TRANSITION_RULES.json` and failure registry as supporting authorities

## Active case
- DMR-009
- File: `combo/bd_hh_rf_r_hit_refresh.png`
- Mode: one image only
- Promotion remains blocked until registration, limb geometry, contact, linework, fixed-drum composite and transition all pass.

## Standard order
CURRENT_STATUS -> SOURCE_AUTHORITY -> REGISTRATION -> ACTIVE_LIMB_CHAIN -> CONTACT_MODE_SELECTION -> OPTIONAL_STRIKE_EXPRESSION -> LINEWORK_CLEANUP -> FIXED_DRUM_COMPOSITE -> TRANSITION -> FINAL_DECISION -> GITHUB_RECORD

## Contact rule
Do not force tip contact or shaft contact. Use `TIP_OR_SHAFT_CONTACT_ADAPTIVE`: choose the contact mode that is visually natural, easiest to preserve, and requires the smallest safe edit.

## Hard rules
- Fixed drum and camera are locked.
- No text-to-image generation.
- Do not solve contact by stretching only the stick when the grip/hand/wrist chain becomes unnatural.
- Contact PASS does not override linework/composite/transition FAIL.
- Do not start a second image in a one-image experiment.
- Every outcome must be written to `CURRENT_STATUS.json` and a case attempt JSON.
