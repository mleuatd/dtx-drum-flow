# Autonomous Execution Boundaries

Status: CURRENT

## May proceed without asking the user
- read latest main and all current-state/master files
- select next queue item
- generate prompts/instructions only
- calculate action keys / limbs / dependencies / risk
- run binary/metadata QA
- generate QA composites, overlays and screenshots
- run validation and regression tests
- generate staging JSON and documentation
- update TODO/IN_PROGRESS/DONE/BLOCKED based on objective gates
- make small commits and push them
- mark clearly image-generation-required work BLOCKED and continue other work

## Requires actual image generation or explicit visual artifact availability
- creating a brand-new character image
- editing an image when no usable source image is present
- final visual acceptance when only machine metadata exists and screenshots/image are unavailable

## Stop only when
- authoritative sources conflict and Git history/ledger cannot resolve them
- required external permissions are unavailable
- tool constraints make the specific operation impossible

One blocked item never stops unrelated work.
