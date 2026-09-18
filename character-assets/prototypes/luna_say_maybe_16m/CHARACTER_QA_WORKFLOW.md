# Character QA / Correction Ledger

This file defines the persistent visual-correction workflow for Luna Say Maybe character frames.

## Source of truth

Machine-readable ledger:

`character-assets/prototypes/luna_say_maybe_16m/CHARACTER_QA_ISSUES.json`

Every new ChatGPT chat or Work session that touches character poses must read that JSON before editing images or runtime mappings.

## Required workflow

1. Review the current GitHub `main` PNG, not an old chat image.
2. Inspect the character by itself and over `layers/drum/drum_base.png`.
3. Check head/face direction, shoulders, elbows, wrists, sticks, waist, hips, knees, ankles, pedal contact, stool position, hair/body transparency, scale/registration, and instrument contact.
4. If a concrete defect is found, append a new issue. Never overwrite or delete history.
5. Use the status flow:
   `PENDING_REVIEW -> OPEN -> IN_PROGRESS -> READY_FOR_REVIEW -> DONE`.
6. Use `WONT_FIX` only after review proves no correction is needed. Record the reason.
7. Use `BLOCKED` when a required binary/tool/environment is unavailable.
8. Record timestamps whenever status changes.
9. Do not mark `DONE` until both:
   - visual re-check passes, and
   - runtime/layer re-check passes.
10. After completion, leave the entry in the ledger permanently.

## Issue fields

Each issue should include:
- `id`
- `createdAt`
- `updatedAt`
- `completedAt`
- `status`
- `severity`
- `assetKey`
- `category`
- `observation`
- `requiredFix`
- `evidence`
- `verification`

## Visual QA categories

Use concrete categories such as:
- anatomy / body-pose
- shoulder-elbow-wrist
- hand-stick-contact
- foot-pedal-contact
- waist-hip-leg
- stool-registration
- hair-body-alpha
- instrument-contact
- layer-order
- scale-registration
- transition-jump
- mobile-layout

## Handoff rule

Before ending a session, update the ledger so the next session can answer:
- what is wrong,
- which asset is affected,
- whether work started,
- what remains,
- how to verify completion.

Do not rely on chat memory for unresolved visual defects.
