# One-by-one image QA

This directory is the current-state authority for single-image repair experiments.

## Active case
- DMR-009
- File: `combo/bd_hh_rf_r_hit_refresh.png`
- Mode: one image only
- Current state: RETRY_REQUIRED / promotion blocked
- Previous evidence: `../donor-mesh-v3/qa/dmr009_contact_reqa_20260921.json`

## Required order
1. Static/global registration: head, hip, stool, body bbox.
2. Torso/posture registration.
3. Active arm/hand/stick geometry.
4. Instrument contact.
5. Fixed-drum composite.
6. Transition against neutral and rebound.

Do not diagnose a contact miss as a stick-only defect until steps 1-3 are complete.

## Hard rules
- Fixed drum and camera are locked.
- No text-to-image generation.
- No formal PNG overwrite from a candidate that has not passed all required QA.
- Do not start another image while DMR-009 is the active one-image experiment.
- Every candidate, rejection, hold, promotion, and final result must be reflected in `CURRENT_STATUS.json` and a case QA JSON.
