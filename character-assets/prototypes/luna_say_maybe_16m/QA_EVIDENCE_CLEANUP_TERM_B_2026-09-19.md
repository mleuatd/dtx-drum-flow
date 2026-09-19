# QA EVIDENCE CLEANUP — TERM-B

Generated: 2026-09-19T20:34:00+09:00
Task: OTHER-002

## Registries reviewed

- character-assets/prototypes/luna_say_maybe_16m/FAILURE_PATTERN_REGISTRY.json
- character-assets/prototypes/luna_say_maybe_16m/REJECTED_ASSET_REGISTRY.json
- active coordination ledger / edit-workspace context

## Findings

1. Historical/failed candidates are already separated from formal runtime assets by NEVER_USE / REJECTED_NEVER_USE / NEVER_USE_AT_RUNTIME status.
2. The two misleading Dropbox aliases for BD+SN remain explicit NEVER_USE entries and must not be imported by filename alone.
3. SN:R rebound_r.png is intentionally retained for history but is NEVER_USE_AT_RUNTIME; runtime policy holds the approved hit frame instead.
4. RC+SN failed redraw candidates remain denied; formal refresh assets are separate and must not be confused with them.
5. LT:R rejected attempts (fresh redraws, malformed local patches, crop failures, minimal-stick failure, arm-rotation failure) are historical QA evidence only and must not be promoted.
6. SN:L TERM-A try01 is a rejected documentation/comparison-sheet misgeneration and must not be reused.
7. Failure registry contains corresponding safeguards for wrong-side instrument, fresh redraw, drum leak, stool/camera drift, rejected reuse, cowlick geometry, line-style over-cleanup, and local-edit full redraw.

## Duplicate/stale disposition

No active CLAIM history or rejection evidence was deleted. Entries without a trustworthy SHA/path remain descriptive deny-list evidence; per registry rules, missing SHA/path must not be inferred. Therefore cleanup is organizational only, not destructive.

## Safety conclusion

Formal/runtime assets must be selected from current inventory/mapping and verified metadata, never from candidate filenames. All NEVER_USE and REJECTED_NEVER_USE records remain preserved.
