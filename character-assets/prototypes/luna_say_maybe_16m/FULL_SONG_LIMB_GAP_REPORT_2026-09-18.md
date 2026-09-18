# Luna Say Maybe full-song limb coverage gap report
Date: 2026-09-18

## Confirmed source state
- FINAL chart: 2,158 notes, measures 1-148.
- Existing authoritative per-note limb sidecar: `site/charts/luna_say_maybe/Luna_say_maybe_1_16_limbs.json`.
- Sidecar scope: measures 1-16 / 144 notes.
- Notes after measure 16: 2,014.
- Embedded `limb`, `hand`, `foot` or animation-limb metadata in those 2,014 notes: 0.
- Repository tree contains no newer/full-song precomputed limb sidecar.

## Existing formal rule source
`character-assets/prototypes/luna_say_maybe_16m/hand_rules.json`

It defines:
- BD -> RF
- LP -> LF
- RC/RD/LC -> R
- SN default -> L
- HH quarter/eighth -> R
- HH sixteenth -> R/L alternating
- tom sequence -> R/L alternating, restart after 360 ms

The file itself is scoped to the 1-16 prototype, so it is not yet a full-song per-note authority.

## Rule replay validation
A deterministic replay of the current rule file over measures 1-16 matches the authoritative 144-note sidecar on every note except one:
- 4.930410s / measure 1 / SN
- generic rule => L
- authoritative phrase-aware assignment => R

That one exception is already documented in the existing limb sidecar: it starts an R-L snare pair so the following right-hand crash remains available.

This means the rule file is a strong basis for extending analysis, but phrase-aware exceptions remain necessary.

## Full-song conflict audit using the existing rules
Applying the existing default rules to measures 17-148 yields 8 simultaneous same-limb conflicts, all involving SN=L plus a tom also landing on L:
- m28 50.469978 SN+FT
- m28 50.901633 SN+FT
- m28 51.333288 SN+FT
- m62 109.175014 SN+FT
- m62 109.606669 SN+FT
- m77 135.937604 SN+LT
- m86 150.613863 SN+FT
- m86 151.045518 SN+FT

Each of those groups contains only the snare and the tom, so a phrase-aware two-hand resolution is required before the sidecar can become authoritative.

## Rapid-snare audit
Measures 17-148 contain 116 SN inter-onset gaps <= 130 ms. The current `hand_rules.json` only says `SN default = L`; it does not codify the required alternating-hand behavior for rapid snare passages or the phrase-aware start-hand decision.

Therefore a mechanically generated full-song sidecar based only on the current JSON would violate the project's no-guessing requirement for these rapid passages.

## Decision
Do not promote renderer inference or a naive generated assignment to authoritative status.

Before refreshed character mapping proceeds past measure 16:
1. extend the formal limb rules to cover rapid SN alternation and phrase-aware start-hand selection;
2. resolve the eight simultaneous SN+tom collisions;
3. generate a full-song per-note sidecar;
4. validate it for same-limb simultaneous conflicts, rapid repeated same-hand hits, and phrase transitions;
5. only then use it as the runtime source of truth.

This report is analysis only; it does not change the live runtime.


## Resolution update — 2026-09-18 19:20 JST

The gap described above is now resolved.

Completed:
- `hand_rules.json` upgraded to version 2 with explicit BD=RF, LP=LF, LB=LF, right-handed cymbal defaults, alternating tom fills, rapid-SN alternation/start-hand policy, and simultaneous-hit conflict policies.
- Full-song generator: `tools/generate-luna-full-limbs.mjs`.
- Validated full-song sidecar: `site/charts/luna_say_maybe/Luna_say_maybe_full_limbs.json`.
- Validation report: `FULL_SONG_LIMB_VALIDATION.json`.
- Limb-aware action inventory: `FULL_SONG_ACTION_KEY_INVENTORY.json`.

Validation result:
- 2,158 / 2,158 notes assigned.
- M1-16 authoritative-prefix mismatches: 0.
- rapid-SN phrases resolved: 64.
- known SN+tom simultaneous conflicts resolved: 8.
- missing limbs: 0.
- simultaneous same-limb conflicts: 0.
- rapid-SN same-hand repeats <=130 ms: 0.
- unresolved groups: 0.

The eight prior SN+tom conflicts were resolved with SN=L and the simultaneous FT/LT=R.

The FINAL chart contains no LP, LB or LC events, so LF is not used by this song's current note data. The formal rules nevertheless define LP/LB=LF for future/runtime correctness.

The earlier DRAFT analysis remains historical evidence only and must not be used as the current authority.
