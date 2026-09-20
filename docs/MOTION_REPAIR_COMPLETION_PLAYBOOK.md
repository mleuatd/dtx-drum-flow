# Motion Repair Completion Playbook

Status: **CURRENT_MANDATORY**

This is the shared operating procedure for repairing existing character motion assets. Every terminal/session that works on `MOTION_DEFECT_BACKLOG.json` must refresh `main` and read this file before claiming or editing an issue.

## 1. Goal and unit of completion

The KPI is **VERIFIED issues**, not candidate count, workflow runs, commits, or machine PASS count.

Work on one issue until it reaches VERIFIED. A hit/rebound pair is one repair unit. Do not abandon a nearly-complete issue to start another unless there is a genuine external blocker.

Formal promotion is not final completion. Required path:

`CLAIM -> best parent -> bounded repair -> machine QA -> exact full-resolution visual QA -> exact promotion -> real-chart runtime QA -> PC QA -> Xperia QA when genuine evidence is available -> validation -> VERIFIED -> release CLAIM`

## 2. Start-of-session protocol

1. Fetch latest GitHub `main`. Never treat chat history as the source of truth.
2. Read:
   - `character-assets/prototypes/luna_say_maybe_16m/MOTION_DEFECT_BACKLOG.json`
   - this playbook
   - `character-assets/prototypes/luna_say_maybe_16m/IMAGE_EDIT_MASTER_RULE.md`
   - `character-assets/prototypes/luna_say_maybe_16m/CHARACTER_GENERATION_PLAYBOOK.json`
   - relevant failure/QA registries only when needed.
3. Respect existing CLAIMs. Do not edit another terminal's claimed issue.
4. Claim one unowned issue. Prefer an issue closest to VERIFIED over opening a fresh broad repair.
5. Immediately begin substantive work; do not stop after writing a plan or queue entry.

## 3. Preserve the original drawing

This is repair, not redraw.

Keep unchanged unless the target action requires it:
- character identity and approximately 4-head chibi proportion;
- three-quarter-back / over-shoulder camera;
- hair, clothing, rough monochrome hand-drawn line style;
- pelvis/stool/body registration;
- fixed drum position, scale and camera;
- every already-correct region.

Do not repaint or regenerate the whole character to fix a local defect.

For a local failure, identify the defect at full resolution and record the smallest practical bounding box. Typical defects include duplicated limbs/sticks, broken hand-to-stick geometry, floating lines, white/rectangular splice fragments, torso/pelvis artifacts, wrong contact, and drum leakage.

## 4. Best-parent rule

Always continue from the **best passing/latest candidate**, not from an older broken source, unless rollback evidence proves the candidate regressed.

After a machine PASS with a visual defect:
1. keep the passing regions fixed;
2. locate the remaining visual defect;
3. repair only that bounded region;
4. re-run QA.

Do not restart with unrelated broad masks merely because visual QA failed.

If the same repair mechanism fails twice, change the mechanism rather than repeating parameter guesses.

## 5. Fast repair loop

For the current issue:

1. Generate/edit the smallest necessary region.
2. Run machine QA.
3. If machine FAIL, identify the exact failing metric/contact and make one targeted correction.
4. If machine PASS, inspect the **exact candidate bytes** at full resolution.
5. Visual QA must check:
   - anatomy and limb count;
   - hand/grip/stick continuity;
   - hair/clothing/line-style consistency;
   - floating/garbage/white fragments;
   - rectangular splice boundaries;
   - torso/pelvis/stool continuity;
   - fixed-drum registration and contamination;
   - target instrument contact;
   - hit -> rebound -> neutral continuity.
6. If visual FAIL, record coordinates/reason and repair that defect on the same best candidate.
7. If visual PASS, promote that exact SHA pair. Never promote a different candidate that merely has the same actionKey.
8. Verify the formal asset SHA/bytes match the reviewed candidate.
9. Proceed immediately to runtime QA.

Machine PASS alone must never set VERIFIED.

## 6. Runtime completion gate

Use the real chart/measure for the action, not only synthetic overlays.

Verify:
- correct action fires at the intended note;
- hit frame is shown;
- rebound follows;
- neutral returns correctly;
- no wrong limb/instrument mapping;
- no visible registration jump or style break;
- no runtime error.

Run repository validation/tests. Record real evidence. PC QA is required where defined by the backlog. Xperia QA may be marked PASS only when genuine device/runtime evidence exists; never fabricate it.

Only after all mandatory gates pass:
- set issue status to `VERIFIED`;
- attach evidence/run IDs/SHAs;
- release CLAIM;
- select the next issue.

## 7. Concurrency rules

Multiple terminals may work in parallel, but never on the same CLAIM.

Before every write/promotion:
1. fetch latest `main`;
2. preserve unrelated changes;
3. rebase/reconcile safely if remote advanced;
4. never force push.

If a promotion push conflicts, do **not** classify the image as failed. Refresh latest main and rerun/reapply the already-approved exact promotion against the new head.

## 8. Efficiency rules

Do:
- prioritize the issue nearest VERIFIED;
- use deterministic local edits;
- reuse already-passing candidate regions;
- batch reads/QA where safe;
- make a repository write only when it advances repair, evidence, or coordination;
- let GitHub Actions handle repeatable validation.

Do not:
- count queue writes, Actions starts, artifacts, or candidates as completion;
- create duplicate workflow runs;
- repeatedly inspect old superseded artifacts;
- perform broad redraws for local defects;
- spend a turn only reporting that a workflow is queued/running when other useful work is possible;
- release a CLAIM before VERIFIED.

## 9. Cross-terminal handoff

The backlog is the coordination ledger. A terminal ending work must leave enough evidence for another terminal to resume without chat history:
- issue/actionKey;
- current status and CLAIM owner;
- best candidate hit/rebound SHA;
- last machine QA;
- last exact visual QA;
- exact remaining defect and coordinates;
- next concrete action;
- relevant run/artifact/commit IDs.

After every ledger write, re-read latest main before choosing the next action.

## 10. Precedence

For motion repair execution, this document controls the **completion workflow**. Existing image master rules still control visual identity and prohibited edits. If an older document encourages advancing to another asset before a visually defective current issue is complete, this playbook takes precedence for the defect-repair backlog.

The operating principle is simple:

**Finish one real issue, preserve everything already correct, and make VERIFIED count go up.**
