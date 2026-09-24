# CB-13 targeted PR repair calibration evidence

This artifact preserves the generated plan and full criterion-level judge
rationale for the one remaining revision 2 targeted-repair pair.

## Run and deterministic validation

- Branch starting head: `8c2a1c4f27b1b42beb995b8250fb01ef28689d2d`.
- Subject: `gpt-6-luna` / high; judge: `gpt-6-sol` / high; one forced repetition.
- Subject/judge calls: 1/1; no retry.
- Case digest: `8e88c1ddfbc611719ab047385313dd2994205c81f767cc695d4cae78f12a1f0a`; run fingerprint: `dcb29629c058506111aaa117fd215ceef4079aad3fbc97afae3c8420e3b4d7d7`.
- The initial validator run failed because the generated plan wrapped its
  `Files and symbols` ownership field across lines. The parser was corrected
  to read that complete field, excluding later verification text.
- `python3.13 evals/run.py regrade --output-dir .scratch/skill-evals/cb13-targeted-repair-20260924`
  reran deterministic grading without model calls. The updated validator
  passes on the preserved generated plan. The subject result and initial
  raw evidence remain unchanged.
- Previous one-function counterexample plan and rationale remain preserved
  in `evals/artifacts/2026-09-24-to-plan-specificity-focused-run.md`.

## Judge result

**Overall: FAIL.** The plan covers and separates both behaviors, but it fails the rubric’s concision requirement through substantial repetition and unrelated contingency sections.

| Criterion | Result | Judge rationale |
| --- | --- | --- |
| `complete-coverage` | PASS | The acceptance table covers both diagnostics and gives each an exact-message test. |
| `baseline-and-red-green` | PASS | Both existing assertions expect unquoted paths. Each slice changes its assertion to the exact quoted output, checks that it fails before the implementation edit, then checks that it passes. |
| `independent-slice-boundaries` | PASS | T1 covers the manifest function and test; T2 covers the profile function and test. Both declare no dependencies. The supplied validator reports zero recognized slices, but the plan text visibly separates them. |
| `concrete-tests` | PASS | The plan names both files, functions, test methods, the spaced path, exact expected messages, focused unittest commands from the repository root, and passing results. |
| `consistent-dependencies` | PASS | T1 and T2 have explicit `none` dependencies. Acceptance rows refer to their matching numbered slices and focused tests. |
| `proportionality` | FAIL | The 126-line plan repeats the same contract across several sections and adds generic repair-budget and re-planning contingencies to a two-call-site change. |
| `planning-boundary` | PASS | The supplied diff shows one new plan file and no source or test edits. The supplied record shows no provider contact. |

## Generated plan

```markdown
<!-- to-plan:conversation-plan:v1 id=c651d594-5941-4c30-8221-a95a5de52fb4 -->

# Quote paths in diagnostic messages

**Planned against:** `main` at `645ee5edc922b74587ed96967eed30e73e43f38c`
**Local state:** Clean

## Approach

Update each diagnostic to wrap its supplied path in single quotes, and update
its existing focused test to assert the complete quoted message using
`configs/team manifest.json`. Keep each function's prefix, public signature,
and path text unchanged.

## Guardrails

- Preserve the prefixes `manifest not found: ` and `invalid profile at `.
- Preserve both public signatures and interpolate the supplied path verbatim,
  including spaces, inside the single quotes.
- Do not change unrelated diagnostics, call sites, or validation behavior.

## Planning decisions

- Keep the manifest and profile changes in separate slices. Their source and
  test files are separate, and each has an existing focused test module, so
  each can be reviewed and validated independently.
- Use the existing tests' space-containing path as the acceptance input. This
  directly verifies that path text remains intact inside the delimiters.

## Implementation context

- **Existing:** `manifest_reader.py` — `missing_manifest_error(path: str) ->
  str` returns `manifest not found: {path}`.
- **Existing:** `profile_loader.py` — `invalid_profile_error(path: str) ->
  str` returns `invalid profile at {path}`.
- **Existing:** `tests/test_manifest_reader.py` —
  `ManifestReaderTest.test_quotes_missing_manifest_path` calls the manifest
  diagnostic with `configs/team manifest.json` and asserts its full result.
- **Existing:** `tests/test_profile_loader.py` —
  `ProfileLoaderTest.test_quotes_invalid_profile_path` calls the profile
  diagnostic with `configs/team manifest.json` and asserts its full result.

## Implementation slices

**Task graph and parallelism:** The graph is acyclic. T1 and T2 are independent
and may run concurrently: they edit distinct source and test files and use
distinct focused unittest modules. No cross-slice wiring or shared mutable file
is required.

### 1. Quote the missing-manifest path

**Task ID:** `T1`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Existing `tests/test_manifest_reader.py` —
`ManifestReaderTest.test_quotes_missing_manifest_path`; existing
`manifest_reader.py` — `missing_manifest_error(path: str) -> str`.
**Test:** First change the test's expected full string to
`manifest not found: 'configs/team manifest.json'`, retaining the input
`configs/team manifest.json`. Before the implementation edit, run the focused
test and confirm it fails because the current message has no quote delimiters.
**Implementation:** In `missing_manifest_error`, retain the signature and
`manifest not found: ` prefix, and put literal single quotes around the
interpolated `path`; do not transform or otherwise alter the path value.
**Validate:** From the repository root, after no setup, run
`python3 -B -m unittest tests.test_manifest_reader`; expect the focused test to
pass with the complete quoted message.
**Complete when:** The focused test passes and the diagnostic returns exactly
`manifest not found: 'configs/team manifest.json'` for its fixture input.

### 2. Quote the invalid-profile path

**Task ID:** `T2`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Existing `tests/test_profile_loader.py` —
`ProfileLoaderTest.test_quotes_invalid_profile_path`; existing
`profile_loader.py` — `invalid_profile_error(path: str) -> str`.
**Test:** First change the test's expected full string to
`invalid profile at 'configs/team manifest.json'`, retaining the input
`configs/team manifest.json`. Before the implementation edit, run the focused
test and confirm it fails because the current message has no quote delimiters.
**Implementation:** In `invalid_profile_error`, retain the signature and
`invalid profile at ` prefix, and put literal single quotes around the
interpolated `path`; do not transform or otherwise alter the path value.
**Validate:** From the repository root, after no setup, run
`python3 -B -m unittest tests.test_profile_loader`; expect the focused test to
pass with the complete quoted message.
**Complete when:** The focused test passes and the diagnostic returns exactly
`invalid profile at 'configs/team manifest.json'` for its fixture input.

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| `missing_manifest_error` retains its public signature and prefix, and encloses the unchanged space-containing path in single quotes. | 1 | From the repository root, `python3 -B -m unittest tests.test_manifest_reader` passes; assert the exact message `manifest not found: 'configs/team manifest.json'`. |
| `invalid_profile_error` retains its public signature and prefix, and encloses the unchanged space-containing path in single quotes. | 2 | From the repository root, `python3 -B -m unittest tests.test_profile_loader` passes; assert the exact message `invalid profile at 'configs/team manifest.json'`. |

## Final validation

- From the repository root, after no setup, run
  `python3 -B -m unittest tests.test_manifest_reader tests.test_profile_loader`;
  expect both exact-message tests to pass.
- From the repository root, after no setup, run the fixture-required command
  `python3 -B -m unittest tests.test_validator`; expect the validator test to
  pass.

## Review focus

- Confirm only the two specified diagnostics gain delimiters: prefixes and
  signatures stay unchanged, and the complete path including its internal
  space remains between the single quotes.

## Allowed deviations

- Within the fixed contract, only a mechanical test-runner or fixture mismatch
  may be repaired after one focused diagnosis pass and at most two repair
  edit-and-validation cycles across unexpected mismatches. Report any repair.

## Re-plan triggers

- Stop for a required signature, prefix, or path-content change; a conflicting
  overlapping baseline change; or a mismatch unresolved within the repair
  budget. Report the evidence, attempted repair and validation, and remaining
  decision or upstream change; do not invoke `to-plan` from the implementation
  worktree.
```

## Limits

- This is one synthetic forced repetition; it does not establish
  repeatability, automatic routing, or production behavior.
- The deterministic ownership and independent-dependency checks pass.
  `proportionality` is explicitly **failed**, not unproven: the judge
  found the 126-line plan repetitive and over-specified for this task.
- The approved remaining model-call budget is exhausted; no further
  subject or judge call was made. A successful proportionality result
  needs a revised plan or calibration budget decision.
