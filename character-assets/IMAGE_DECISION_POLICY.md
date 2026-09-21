# DTX Drum Flow — Character Image Decision Policy

Version: 1.0
Status: ACTIVE

## 0. Purpose
This file defines how to derive the editing method from the requested motion instead of hard-coding a method per image.

## 1. Parse the target first
Resolve:
- phase
- right-hand action
- left-hand action
- right-foot action
- left-foot action
- simultaneous actions
- protected regions
- paired asset / read-only constraints

Then state one sentence:
"What must this image clearly look like it is doing?"

## 2. Choose primary and secondary actions
The primary action is the action whose visual correctness defines the frame.
Secondary actions are added without degrading the primary action.

Typical rule:
- hand strike + BD foot: hand strike is primary, BD foot is secondary
- two-hand strike: choose an existing complete combo if available; otherwise choose the stronger completed donor as parent and add the second limb locally
- foot-only action: foot action may be primary

## 3. Search completed donors before editing
Donor ranking:
A. same instrument + same limb + same phase + VERIFIED/PASS
B. same instrument + same limb + same phase + visually accepted
C. same instrument/limb with near phase
D. closest natural pose
E. neutral/base

If A/B exists, do not jump directly to D/E plus large reconstruction.

## 4. Inspect the completed donor itself
Before transforming a supposedly completed donor:
- composite it with the locked drum in the same coordinate system
- inspect actual full-resolution image
- confirm what instrument it visually strikes
- confirm hand/stick/contact/anatomy

If a numeric detector disagrees with an obviously correct completed donor, verify the detector before rejecting the donor. Diff/alpha-derived "tip" pixels can be wrong.

## 5. Parent selection
If a completed primary-action donor exists, make it the first parent candidate.
For combos, add only the missing secondary action from a suitable donor.

Example:
HH:R hit + BD:RF
→ parent = completed HH:R hit
→ secondary overlay = BD:RF lower-body action
→ protect completed HH arm/hand/stick relationship

## 6. Region ownership
Before compositing multiple donors, assign one owner per region:
- head/hair/torso
- each upper arm/forearm/hand/stick
- each leg/foot
- stool
- drum/background

Do not let two sources own the same active-limb region; this prevents ghosts and duplicated geometry.

## 7. Direct donor test comes first
If donors share registration:
1. composite without warp
2. fixed-drum review
3. numeric QA
4. AI visual QA

If it passes, stop editing.

## 8. Escalation tree
If direct donor fails:

A. seam/boundary only
→ mask/blend/local cleanup

B. small contact or grip mismatch
→ local wrist/grip/stick or joint correction

C. local shoulder/limb direction mismatch
→ bone-local transform or narrow local mesh

D. donor pose fundamentally wrong
→ reselect donor

Do not use a huge warp to turn the wrong donor into the right donor.

## 9. Mesh rules
Mesh is permitted only when:
- donor identity/action is correct
- direct composite cannot satisfy target
- required deformation is limited
- protected regions remain locked

Prefer bone/segment-local transforms over whole-limb RBF when large pose changes would create holes/ghosting.

Stop the current mesh strategy on:
- banding
- holes
- double limb
- rectangular artifact
- detached hand
- broken stick
- unnatural shoulder/elbow

Then return to donor selection/direct composite/local transform.

## 10. Local AI edit
Use local AI editing only for an existing correct structure that needs a small visual repair:
- seam
- missing/broken line
- small hand-stick connection issue
- small local contour defect

Do not use it to invent the whole pose, choose the struck instrument, or regenerate the person.

## 11. Contact and stick
Use DRUM_GEOMETRY / current authoritative geometry.
Maintain standard stick length/tolerance defined by the work order or geometry.
If reach fails, adjust/reselect arm chain; never simply lengthen stick.

## 11A. Rigid-stick and wrist-alignment gate

Before a candidate can pass:
- grip→tip must be a single straight rigid shaft
- the shaft must be continuous and unbroken
- no local direction change is allowed anywhere between grip and tip
- wrist→grip orientation must plausibly support the stick axis
- forearm→wrist→hand must not look twisted merely to preserve an old donor pose

If straight-stick geometry and wrist anatomy conflict, preserve the rigid stick and re-solve the wrist/forearm/elbow chain or reselect the donor.

Numeric QA should record at least:
- stickAxisAngle
- stickAxisStraightness / residual
- stickContinuity
- wristToGripVsStickAxisDelta
- existing wrist deviation and elbow angle

A visually bent/broken stick is FAIL even if contact, length and target angle pass.

## 12. Required visual loop
After donor composite, mesh, local transform, or AI edit:
- inspect actual candidate
- inspect fixed-drum composite
- inspect focused crop if useful
- inspect transition when required

Ask:
1. What does it look like she is striking?
2. Is that the requested instrument?
3. Is stick contact clear and natural?
4. Is stick length/direction credible?
5. Is shoulder→elbow→wrist→hand→stick continuous?
6. Are there ghosts, holes, duplicated geometry or rectangular seams?
7. Did the secondary action damage the primary action?

Numeric PASS + visual FAIL = FAIL.

## 13. Multi-hit guidance
For HH+SN / RD+SN / RC+SN:
- prefer an already accepted combo
- otherwise choose the best completed primary donor
- add the other limb locally
- avoid changing both arms wholesale unless no correct donor exists

For BD + hand action:
- hand action normally remains primary
- overlay only the required BD leg/foot region
- verify leg→ankle→foot→pedal continuity

## 14. Rebound
Evaluate neutral→hit→rebound→neutral.
A rebound may be locally correct but transitionally wrong.
Respect READ_ONLY pair constraints.

## 15. Method selection tie-break
When multiple methods can work, prefer:
1. more preservation of already-approved pixels
2. smaller edit area
3. lower risk to primary action
4. stronger approved donor evidence
5. easier numeric verification
6. easier visual verification
7. reproducibility
8. speed

At equal quality, choose the faster method.

## 16. Final decision questions
Always answer in order:
1. What action must this frame communicate?
2. Does a completed version of that action already exist?
3. Can that completed image be the parent?
4. Can missing secondary actions be added without changing the primary action?
5. Can it work with zero deformation?
6. If not, exactly which small region fails?
7. What is the least destructive correction?
8. Does numeric QA pass?
9. Does the actual image look natural?
10. Does the transition remain natural?
