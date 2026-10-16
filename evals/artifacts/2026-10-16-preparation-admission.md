# Preparation admission rule review

## Evidence and limit

The user reports that Haze fallback transparency waited 3h36m for optics to
merge because its accepted plan required an integrated baseline and both changes
touched rendering files. Later local implementation and qualification took
about 32 minutes. These are supplied observations, not independently reconstructed
timings. They establish a reason to inspect admission granularity; they do not
show which preparation existed or how much wait could have been recovered.

## Inspected rules

- `run-github-project/references/drain-scheduler.md`, Conflict Admission Gate,
  already allowed independently testable disjoint slices, but its first rule
  delayed a whole candidate for an explicit plan prerequisite on occupied work.
- `to-plan/references/workflow.md` already separated observable increments and
  slice/final checks, but treated shared mutable files as making tasks
  non-independent without distinguishing earlier preparation from those edits.
- Both delivery procedures correctly held dependent tasks until prerequisite
  integration and affected checks. Those gates remain.

## Bounded change

Classify behavioral prerequisites, shared-file mutation conflicts and final
integration requirements separately. Permit only explicitly plan-backed,
independently testable preparation on the committed integrated base, with slice
owner, paths/resources, focused check and a stop before shared edits or dependent
behavior. Preserve whole-ticket native dependencies, accepted ordering, canonical
whole-file locks, resource grants, older-first integration and final validation.
An accepted all-work baseline prerequisite needs an authorized plan change;
dispatch cannot reinterpret it. Unknown seams remain held for investigation.

This makes earlier preparation possible when evidence supports it. It does not
establish that the original fallback plan permitted it, authorize shared rendering
edits early, add stacked PR infrastructure, or estimate recoverable wait time.

## Deterministic coverage

Three calibration cases check normalized report fields using the existing text
validator: independent fixture preparation (plus a native-blocker variant), a
decoder-dependent exporter (plus an accepted all-work prerequisite), and an
uncertain alpha-contract seam (plus discovered overlap at a clean checkpoint).
Tests accept the expected reports and reject missing fields and changed decisions,
including expanded paths, skipped stops, early qualification and stolen grants.
These checks exercise the offline artifact contract, not model adherence to prose.
No live model evaluations are required or authorized by this change.

Validation passed: `npm run lint`, `npm run build`, `npm run evals:validate`
(194 cases), and `npm test` (7 Node tests, 238 script tests with one skip,
and 373 evaluation-harness tests). The admission test also rejects contradictory
field lines. No versions, published artifacts or remote state were changed.
