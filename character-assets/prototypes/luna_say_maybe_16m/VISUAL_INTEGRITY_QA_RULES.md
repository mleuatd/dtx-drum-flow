# VISUAL_INTEGRITY_QA_RULES

Updated: 2026-09-20T06:13:00+09:00

## Purpose

This is the mandatory visual-integrity gate for Luna Say Maybe character-frame repair and promotion.

Pixel locality, ROI containment, SHA identity, bbox/centroid stability and registration checks remain required, but they are never sufficient by themselves. A frame must also be natural as a human pose, coherent as line art, and semantically correct when composited with the fixed drum layer.

## Mandatory review axes

### Human anatomy

Review the complete visible chain relevant to the pose:
- pelvis -> thigh -> knee -> shin -> ankle -> foot -> toe/boot
- shoulder -> elbow -> wrist -> hand -> stick
- front/back ordering of paired limbs
- seated balance and seat contact
- active-limb motion direction for strike/pedal semantics

Hard FAIL if any chain becomes unreadable, disconnected, anatomically implausible, or contradictory to the intended action.

### Linework

Hard FAIL for:
- broken/interrupted stick
- hand-to-stick disconnect
- implausible stick direction/length/tip
- unexplained waist/pelvis/skirt/seat lines
- line dropout
- accidental double stroke
- isolated/short/crossing artifact lines
- layer-derived stray lines
- any extra line that corrupts silhouette or body reading

### Fixed-drum composite

Every candidate must be checked over the approved fixed drum layer at x=0,y=0, scale=1.

Hard FAIL if:
- stick tip does not read as reaching the intended strike surface
- active foot does not read as engaging the intended pedal
- person/drum front-back order is contradictory
- stool/seat/legs/drum overlap is physically implausible
- the pose does not read as a viable drum-playing action
- a frame that looks acceptable alone becomes anatomically or semantically wrong in composite

## Promotion rule

A candidate cannot become VERIFIED or APPROVED_LIVE unless all of the following are explicitly PASS:
1. source/SHA/canvas/alpha integrity
2. ROI/locked-region constraints
3. human anatomy QA
4. linework QA
5. fixed-drum composite QA
6. runtime before/hit/rebound/after visual coherence
7. neighbor regression QA

Any missing mandatory axis means the state must remain one of:
- NEEDS_VISUAL_REVIEW
- NEEDS_HUMAN_ANATOMY_QA
- NEEDS_LINEWORK_QA
- NEEDS_FIXED_DRUM_COMPOSITE_QA
- FIXED_PENDING_RUNTIME_QA

## Measurement additions

Repair specs should measure or explicitly mark NEEDS_MEASUREMENT for:
- hip / pelvis
- knee
- ankle
- foot / toe / boot connection
- seat edge and seat-contact overlap
- shoulder / elbow / wrist / hand
- stick grip line and stick tip
- relevant drum/pedal contact point

No unmeasured geometry or tolerance may be invented.

## Required lesson from 2026-09-20 review

Previous QA over-weighted changed-pixel and ROI locality and did not reliably reject visible human-anatomy failures, broken sticks, or stray waist/seat lines. Those are now first-class defects and mandatory hard-gate failures.
