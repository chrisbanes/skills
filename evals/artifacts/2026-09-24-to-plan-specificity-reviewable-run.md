# Repaired `to-plan` specificity run: plans and judge evidence

This artifact preserves the generated plan text and criterion-level judge
evidence so the run can be reviewed without access to the ignored raw run
directory. Model calls were run once each in the forced arm; deterministic
regrading did not make additional model calls.

## Run controls and grading

- Branch at run: `agent/big-head/fbf8fb9abafb`, skill source commit
  `c37370231a5537e7ab9b7dd51328d96ec92ced9c`.
- Subject: `gpt-6-luna` / high; judge: `gpt-6-sol` / high.
- Codex CLI: `codex-cli 0.155.1`; one repetition per case.
- Budget used: two subject and two judge calls; no retries or process
  failures. The harness estimate used `$0.25` subject and `$1.00` judge per
  call (`$2.50` total); these are estimate inputs, not billed usage.
- Raw results SHA-256: `42f22525e90086f5d3278aee5d3e5ec47020ea6d864fb190096a17e7896bb489`.
- After the run, deterministic expectations were aligned with the task:
  the calibration no longer requires an optional helper symbol, and the
  counterexample relies on its task-graph acyclicity validator rather than
  a case-sensitive literal spelling. `evals/run.py regrade` reapplied only
  local checks; the original judge outputs were preserved.

## Revised two-diagnostic calibration

- Record: `to-plan-specificity-calibration:forced:1`.
- Case digest at execution: `5b94419186945064bcc3707b6d104145d742b343008c3618d536067c6df32dfb`.
- Case digest used for local regrade: `e10036b0f97d447651cbdf6c5ce6a1227f661b0086bda669f14393df9a196be1`.
- Run fingerprint: `de4228b797379d9e6b0ab1c302175347cca61e9a0ddb3a92c9b21e4ac8006e22`.
- Structural/objective validation after regrade: **PASS**; judge: **PASS**.
- Judge rationale: The supplied plan meets the stated coverage, test, dependency, and planning-boundary criteria. The separate validator message asks for symbols absent from the stated repository task, so it does not change this judgment.

### Criterion evidence

- **complete-coverage: PASS.** The acceptance table covers both diagnostic functions and ties each exact-output assertion to the implementation slice.
- **baseline-and-red-green: PASS.** The plan identifies both existing unquoted assertions, changes their expected strings, and calls for observing both focused tests fail before the implementation edits and pass afterward.
- **concrete-tests: PASS.** It names the files, functions, test methods, spaced-path input, exact quoted outputs, repository-root commands, and expected OK results.
- **consistent-dependencies: PASS.** The single declared slice has task ID T1 and an explicit dependency of none. Acceptance rows reference that slice and its verification.
- **proportionality: PASS.** One slice groups the two small changes by their shared formatting behavior. The specified validator command follows the fixture instruction.
- **planning-boundary: PASS.** The supplied diff shows one new local plan and no source or test edits. The supplied record shows no provider contact.

### Generated plan

```markdown
<!-- to-plan:conversation-plan:v1 id=2c650617-256b-4b2b-810b-0e9f7c8dcbeb -->

# Quote paths in diagnostics

**Planned against:** `main` at `307edf136d64dda3b28bde754b3b73142c9b9cbd`
**Local state:** Clean

## Approach

Update both diagnostic functions to wrap the supplied path in single quotes. Update their unit tests to assert the exact new diagnostic strings, including a path with an internal space.

## Guardrails

- Preserve each public function signature, diagnostic prefix, and supplied path text exactly; only add single quotes around the path.
- Do not change unrelated diagnostics or behavior.

## Planning decisions

- Keep both functions and their focused tests in one slice: this is one small, user-visible formatting contract, and each test checks the same path-with-space example.
- The existing test methods already use `configs/team manifest.json` and assert the complete output, so update their expected strings to include the quotes and retain that input unchanged.

## Implementation context

- **Existing:** `manifest_reader.py` — `missing_manifest_error(path: str)` returns `manifest not found: {path}`.
- **Existing:** `profile_loader.py` — `invalid_profile_error(path: str)` returns `invalid profile at {path}`.
- **Existing:** `tests/test_manifest_reader.py` — `ManifestReaderTest.test_quotes_missing_manifest_path` checks the exact message for `configs/team manifest.json`.
- **Existing:** `tests/test_profile_loader.py` — `ProfileLoaderTest.test_quotes_invalid_profile_path` checks the exact message for `configs/team manifest.json`.

## Implementation slices

**Task graph and parallelism:** The graph has one root task and is acyclic. There is one slice; no parallel work is needed because the four files together implement and verify one formatting contract.

### 1. Quote supplied paths in both diagnostics

**Task ID:** `T1`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Edit existing `tests/test_manifest_reader.py` (`ManifestReaderTest.test_quotes_missing_manifest_path`) and `tests/test_profile_loader.py` (`ProfileLoaderTest.test_quotes_invalid_profile_path`) to expect the quoted strings. Edit existing `manifest_reader.py` (`missing_manifest_error`) and `profile_loader.py` (`invalid_profile_error`) to produce those strings. No new files or symbols.
**Test:** First change the expected output in each existing test while keeping the input `configs/team manifest.json`. Run from the repository root: `python3 -B -m unittest tests.test_manifest_reader tests.test_profile_loader`. Before the implementation edits, both focused tests should fail because the actual diagnostic lacks the single quotes; after the edits, assert exact outputs `manifest not found: 'configs/team manifest.json'` and `invalid profile at 'configs/team manifest.json'`.
**Implementation:** After confirming the test-first failures, change only the f-string formatting in `manifest_reader.py` and `profile_loader.py` to place a literal single quote immediately before and after `{path}`. Keep function names, `path: str` parameters, return annotations, prefixes (`manifest not found:` and `invalid profile at`), and path content unchanged.
**Validate:** From the repository root, with no setup, run `python3 -B -m unittest tests.test_manifest_reader tests.test_profile_loader`; expect both tests to pass and report `OK`.
**Complete when:** Both exact-output tests pass and the outputs retain the complete path, including its space, between single quotes.

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| `missing_manifest_error` returns the unchanged `manifest not found:` prefix followed by the full supplied path in single quotes, preserving the space in `configs/team manifest.json`. | 1 | `python3 -B -m unittest tests.test_manifest_reader tests.test_profile_loader`; `ManifestReaderTest.test_quotes_missing_manifest_path` asserts exact output `manifest not found: 'configs/team manifest.json'`. |
| `invalid_profile_error` returns the unchanged `invalid profile at` prefix followed by the full supplied path in single quotes, preserving the space in `configs/team manifest.json`. | 1 | `python3 -B -m unittest tests.test_manifest_reader tests.test_profile_loader`; `ProfileLoaderTest.test_quotes_invalid_profile_path` asserts exact output `invalid profile at 'configs/team manifest.json'`. |
| The repository's required validator check remains green. | 1 | `python3 -B -m unittest tests.test_validator`; expect the test to pass and report `OK`. |

## Final validation

- From the repository root, with no setup, run `python3 -B -m unittest tests.test_manifest_reader tests.test_profile_loader`; expect both targeted tests to pass and report `OK`.
- From the repository root, with no setup, run `python3 -B -m unittest tests.test_validator`; expect the repository-required validator test to pass and report `OK`.

## Review focus

- Check that each prefix and path are byte-for-byte unchanged apart from the two surrounding single quotes, and that the internal space remains inside the quotes.

## Allowed deviations

- Within the fixed contract, only mechanical adjustments needed to keep the stated test command valid may be repaired after one focused diagnosis pass and at most two repair edit-and-validation cycles across unexpected mismatches; report any repair.

## Re-plan triggers

- Stop for a required change to either public signature, prefix, path text, or scope; an overlapping baseline change; or a test-command mismatch unresolved within the repair budget. Report the evidence, attempted repair and validation, and remaining decision or upstream change; do not invoke `to-plan` from the implementation worktree.
```

## Existing one-function counterexample

- Record: `to-plan-authorized-draft-direct:forced:1`.
- Case digest at execution: `653b65ff0aca5b3b0d82653b9ac82414d8cec435c01cac13a904acdbfef17b69`.
- Case digest used for local regrade: `bd27f313243844f9e078918802013721570e890cfd5c818fbff8ff2f30e4f168`.
- Run fingerprint: `7d13e02578ed8285b44a380d268d1424e19f042556336bfbf5119c28b2c4a6a2`.
- Structural/objective validation after regrade: **PASS**; judge: **PASS**.
- Judge rationale: The supplied plan meets the authoritative rubric. The supporting JSON reports a validator failure for the lowercase token “acyclic”; the plan expresses that condition as “Acyclic single-task graph,” so that report does not establish a substantive rubric failure.

### Criterion evidence

- **local-draft: PASS.** The supplied diff shows one locally marked plan under .scratch/to-plan/, with no confirmation request.
- **executable-plan: PASS.** The plan names validator.py, tests/test_validator.py, and their existing symbols. It orders an exact assertion for settings file.json, an expected failing run, the formatting edit, and a passing focused run from the repository root.
- **proportionality: PASS.** The plan contains one implementation slice and no separate proof prerequisite or speculative implementation branches.
- **executor-readiness: PASS.** The edit and validation steps are specified. Allowed deviations are set to none, and the plan says to stop if the focused test still fails after the planned edit.
- **publication-boundary: PASS.** The supplied diff shows a local plan and explicitly excludes publishing or contacting a provider.

### Generated plan

```markdown
<!-- to-plan:conversation-plan:v1 id=41cc4081-3bfd-45de-8b94-92266ed6a9f1 -->

# Quote missing validator files

**Planned against:** `main` at `1e72b8e4cab52c85cf94a1c1fd1a8b4c3106a78a`
**Local state:** Clean

## Approach

Strengthen the existing unit test to require the exact diagnostic with a spaced path in quotes, observe it fail, then change `missing_file_error` to format the supplied path with its Python quoted representation.

## Guardrails

- Preserve the public `missing_file_error(path: str) -> str` signature and `missing file: ` prefix.
- Limit implementation edits to `validator.py` and `tests/test_validator.py`; do not publish or contact a provider.

## Planning decisions

- Use `path!r` so Python supplies a quoted representation that retains spaces; the specified input produces `missing file: 'settings file.json'`.
- Run the test-first red and green checks from the repository root using the fixture-mandated command. The unchanged baseline currently passes.

## Implementation context

- **Existing:** `validator.py` — `missing_file_error` currently returns `f"missing file: {path}"`; preserve its interface and add quoted formatting at this helper.
- **Existing:** `tests/test_validator.py` — `ValidatorTest.test_names_missing_file` currently checks only that `settings.json` occurs; replace that weak assertion with an exact diagnostic assertion for `settings file.json`.

## Implementation slices

**Task graph and parallelism:** Acyclic single-task graph (`T1`, no dependencies); no tasks can run concurrently because the test and implementation edits form one test-first sequence.

### 1. Quote the missing path

**Task ID:** `T1`
**Depends on:** `none`
**Prerequisites:** None; baseline `python3 -B -m unittest tests.test_validator` passes from the repository root.
**Files and symbols:** Edit `tests/test_validator.py` at `ValidatorTest.test_names_missing_file` and `validator.py` at `missing_file_error`; create no files or symbols.
**Test:** In `tests/test_validator.py`, call `missing_file_error("settings file.json")` and assert equality with `"missing file: 'settings file.json'"`. Run `python3 -B -m unittest tests.test_validator` from the repository root before changing the implementation; expect a failing assertion because the current result omits quotes.
**Implementation:** After observing the red test, change only the helper’s formatting to `f"missing file: {path!r}"`; retain its name, parameter, annotation, return annotation, and prefix. Keep the exact-output assertion as the regression test.
**Validate:** From the repository root, run `python3 -B -m unittest tests.test_validator`; expect the focused test to pass (`Ran 1 test`, `OK`).
**Complete when:** The test checks the exact quoted diagnostic including the space, the implementation preserves the signature, and the focused command passes.

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| Diagnostic preserves `settings file.json`, including its space, inside quotes after `missing file: `. | 1 | Exact equality assertion in `tests.test_validator`; `python3 -B -m unittest tests.test_validator` passes. |
| Public `missing_file_error` signature remains unchanged. | 1 | Review `validator.py` and confirm `def missing_file_error(path: str) -> str` is unchanged. |

## Final validation

- From the repository root, after the red test and implementation edit, run `python3 -B -m unittest tests.test_validator`; expect `Ran 1 test` and `OK`.

## Review focus

- Confirm the single quotes are part of the exact diagnostic and the supplied spaces are preserved.

## Allowed deviations

- None; retain the stated output, scope, test seam, and validation command.

## Re-plan triggers

- Stop if the required quoted output or public signature cannot be implemented within the two named files, if the baseline changes overlap either file, or if the focused test remains failing after the planned edit. Report the evidence and required contract or upstream change.
```

## Limits

The calibration is synthetic and has one forced observation. It supports
the stated behavior for these case versions, but does not establish
repeatability, automatic routing, or production behavior. The advisory
scorecard excludes calibration cases from benchmark gates.
