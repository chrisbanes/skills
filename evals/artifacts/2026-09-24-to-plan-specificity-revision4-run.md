# CB-13 revision 4 final calibration evidence

This artifact preserves the complete generated plans and every judge criterion rationale from the two approved forced pairs. Neither prior judge result was relabeled. The run used exactly two subject calls and two judge calls, with no retries.

## Deterministic prechecks

- `python3.13 -m unittest evals.tests.test_workflows_writing_matrix`: 28 tests passed. This includes current unquoted fixture assertions, separate independent slices, old verbose-plan rejection, a concise plan with an Approach summary accepted, and unchanged dependency constraints.
- `python3.13 evals/run.py validate --suite workflows-writing`: all 38 cases validated.
- `npm run lint`: passed.
- `git diff --check`: passed before and after the model runs.
- Both preserved revision 3 plans were revalidated directly: 126-line verbose plan rejected for generic `Allowed deviations` and `Re-plan triggers`; 65-line concise plan accepted.
- Fixture baseline was inspected: `missing_manifest_error` and `invalid_profile_error` both return unquoted path text. Prompt remains task-centered without prescribing slice count/order or a test sequence. Rubric allows a brief Approach summary. Separate slice ownership and dependency rules remain in force.
- The one-function case was independently planned with the same pinned models and exactly one forced repetition; plan preview confirmed exactly one subject and one judge call.

## Run controls

- Subject: `gpt-6-luna` / high. Judge: `gpt-6-sol` / high. Forced arm, one repetition for each case.
- Cost assumptions supplied to harness: $0.25 per subject and $1.00 per judge call ($2.50 estimated total, not billed usage).
- Raw result hashes and run identifiers are listed below. Existing revision 3 evidence remains in `2026-09-24-to-plan-specificity-revision3-run.md`; the earlier one-function counterexample remains in `2026-09-24-to-plan-specificity-reviewable-run.md`.

## Two-slice calibration

- Record: `to-plan-specificity-calibration:forced:1`.
- Case digest: `16ff38e5b3c352aa24f90178483c8498a9cd59a11e31ce063b342440b8afc948`.
- Run fingerprint: `c7285c40094038e9e1b33a4123b82f49513c2f639135628c85f330d652e76a25`.
- Raw `results.json` SHA-256: `7ad9c3715386d0c2dfb291f988b7be345923096f264aeba3d545e2fd25670741`.
- Deterministic validator: PASS (`validated to-plan-specificity-calibration`).
- Judge overall: **FAIL**.
- Subject/judge retries: 0.

### Criterion results

| Criterion | Result | Judge rationale |
| --- | --- | --- |
| `complete-coverage` | PASS | Both acceptance rows map a requested diagnostic to its own slice and focused test. |
| `baseline-and-red-green` | PASS | Each slice changes the existing assertion to the exact quoted output, runs it to observe failure against the current unquoted formatter, then reruns it after implementation. |
| `independent-slice-boundaries` | PASS | T1 covers the missing-manifest formatter and test; T2 covers the invalid-profile formatter and test. Both declare no dependencies. |
| `concrete-tests` | PASS | The plan names both files, functions, test methods, the spaced-path input, exact expected messages, focused unittest commands, repository-root working directory, and expected passing results. |
| `consistent-dependencies` | PASS | T1 and T2 have stable IDs and explicit `none` dependencies; acceptance rows point to their respective slices and tests. |
| `proportionality` | FAIL | The shared preservation requirements and spaced-path check recur in Guardrails, Planning decisions, both slice descriptions, completion conditions, and acceptance rows. This repeats contract detail across planning sections beyond the brief Approach summary allowed by the criterion. |
| `planning-boundary` | PASS | The supplied workspace diff adds one plan file only; it shows no source or test edits or provider contact. |

### Full generated plan

```markdown
<!-- to-plan:conversation-plan:v1 id=b6ced9d3-b34b-432e-bd9d-6e158b333d03 -->

# Quote paths in error diagnostics

**Planned against:** `main` at `cdeb6c859f13c8fe609bd1ed0143602d08c7ac1e`
**Local state:** Clean

## Approach

Update each diagnostic formatter to surround its supplied path with single quotes, and update its focused unit test to assert the complete quoted message.

## Guardrails

- Preserve each diagnostic prefix, public function signature, and path text exactly; keep spaces inside the quotes.
- Limit implementation edits to the two formatter modules and their corresponding tests.

## Planning decisions

- Keep the formatters in separate slices: each has its own module, direct unit test, and focused command, with no dependency on the other formatter.
- Use the existing tests with `configs/team manifest.json` to verify the space remains part of the path while quotes surround the full path.

## Implementation context

- **Existing:** `manifest_reader.py` — `missing_manifest_error(path: str) -> str` returns `manifest not found: {path}`.
- **Existing:** `profile_loader.py` — `invalid_profile_error(path: str) -> str` returns `invalid profile at {path}`.
- **Existing:** `tests/test_manifest_reader.py` — `ManifestReaderTest.test_quotes_missing_manifest_path` checks the complete output for `configs/team manifest.json`.
- **Existing:** `tests/test_profile_loader.py` — `ProfileLoaderTest.test_quotes_invalid_profile_path` checks the complete output for `configs/team manifest.json`.

## Implementation slices

**Task graph and parallelism:** The graph is acyclic. T1 and T2 are independent and may run concurrently because they edit distinct modules and test files. No shared-file integration is required.

### 1. Quote the missing manifest path

**Task ID:** `T1`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** `tests/test_manifest_reader.py` — `ManifestReaderTest.test_quotes_missing_manifest_path`; `manifest_reader.py` — `missing_manifest_error`.
**Test:** First change the expected complete string for input `configs/team manifest.json` to `manifest not found: 'configs/team manifest.json'`, retaining the existing call and assertion. Run the focused command before changing the formatter; it should fail because the current output has no quotes. The test asserts both the preserved prefix and the exact path, including its internal space.
**Implementation:** After observing that red failure, change only the returned f-string in `missing_manifest_error` to put literal single quotes around `{path}`. Preserve the signature and `manifest not found:` prefix, and do not transform the supplied path.
**Validate:** From the repository root (`.`), after the assertion update and formatter edit, run `python3 -B -m unittest tests.test_manifest_reader`; expect the test to pass with the complete quoted diagnostic.
**Complete when:** The focused test passes and `missing_manifest_error("configs/team manifest.json")` returns exactly `manifest not found: 'configs/team manifest.json'`.

### 2. Quote the invalid profile path

**Task ID:** `T2`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** `tests/test_profile_loader.py` — `ProfileLoaderTest.test_quotes_invalid_profile_path`; `profile_loader.py` — `invalid_profile_error`.
**Test:** First change the expected complete string for input `configs/team manifest.json` to `invalid profile at 'configs/team manifest.json'`, retaining the existing call and assertion. Run the focused command before changing the formatter; it should fail because the current output has no quotes. The test asserts both the preserved prefix and the exact path, including its internal space.
**Implementation:** After observing that red failure, change only the returned f-string in `invalid_profile_error` to put literal single quotes around `{path}`. Preserve the signature and `invalid profile at` prefix, and do not transform the supplied path.
**Validate:** From the repository root (`.`), after the assertion update and formatter edit, run `python3 -B -m unittest tests.test_profile_loader`; expect the test to pass with the complete quoted diagnostic.
**Complete when:** The focused test passes and `invalid_profile_error("configs/team manifest.json")` returns exactly `invalid profile at 'configs/team manifest.json'`.

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| Missing-manifest diagnostic preserves its prefix and path while enclosing `configs/team manifest.json` in single quotes. | 1 | `ManifestReaderTest.test_quotes_missing_manifest_path` in the focused command. |
| Invalid-profile diagnostic preserves its prefix and path while enclosing `configs/team manifest.json` in single quotes. | 2 | `ProfileLoaderTest.test_quotes_invalid_profile_path` in the focused command. |

## Final validation

- From the repository root (`.`), after both slices are complete, run `python3 -B -m unittest tests.test_validator`; expect the validator test suite to pass. This is the repository fixture's required implementation validation command; the two focused slice commands verify the changed diagnostics.
```

Judge summary: The plan covers both behaviors with independent, testable slices and stays within the planning boundary, but its repeated contract detail fails the proportionality criterion.


## One-function counterexample

- Record: `to-plan-authorized-draft-direct:forced:1`.
- Case digest: `bd27f313243844f9e078918802013721570e890cfd5c818fbff8ff2f30e4f168`.
- Run fingerprint: `2922274b85af5e5f8ac19779317f3705e396d31b250d372f3b3cbc9ac9273d1e`.
- Raw `results.json` SHA-256: `1ad4eb2c1d700f02d45e406c396f332ffce02288f6e7903f9456dbc3d2716669`.
- Deterministic validator: PASS (`validated to-plan-authorized-draft-direct`).
- Judge overall: **FAIL**.
- Subject/judge retries: 0.

### Criterion results

| Criterion | Result | Judge rationale |
| --- | --- | --- |
| `local-draft` | PASS | The workspace diff shows one marked plan under .scratch/to-plan/; no confirmation request is shown. |
| `executable-plan` | PASS | The plan names validator.py, tests/test_validator.py, and their symbols; specifies the exact assertion for settings file.json, the expected failing test, the repository-root command, the implementation edit, and the passing acceptance condition. |
| `proportionality` | PASS | The plan has one implementation slice for the existing function and test, with no speculative proof task or prerequisite. |
| `executor-readiness` | FAIL | The edit sequence is specified, but the plan gives no explicit diagnosis or edit-validation budget for autonomous repair. |
| `publication-boundary` | PASS | The diff contains only a local plan. The supplied evidence shows no publication or remote-provider contact. |

### Full generated plan

```markdown
<!-- to-plan:conversation-plan:v1 id=2dbc6591-c97d-46de-bd11-eb0caa0aa4ca -->

# Quote missing validator files

**Planned against:** `main` at `be9530ff9d0a64f0269fa6ef6b802b74a72e1e42`
**Local state:** Clean

## Approach

Update the existing unit test first to require the exact quoted diagnostic for a path containing spaces, observe it fail, then quote the supplied path in `missing_file_error` and rerun the focused test.

## Guardrails

- Preserve the public `missing_file_error(path: str) -> str` signature and its `missing file: ` prefix.
- Limit implementation edits to `validator.py` and `tests/test_validator.py`; do not publish or contact a provider.

## Planning decisions

- Assert the full diagnostic `missing file: "settings file.json"` so the test checks both the unchanged prefix and the spaces-preserving quoted path.

## Implementation context

- **Existing:** `validator.py` — `missing_file_error` returns the current `missing file: {path}` diagnostic.
- **Existing:** `tests/test_validator.py` — `ValidatorTest.test_names_missing_file` currently checks only that `settings.json` occurs in the result.

## Implementation slices

**Task graph and parallelism:** One acyclic task, `T1`; no parallel tasks because the test and implementation edit the same behavior contract.

### 1. Quote missing file paths

**Task ID:** `T1`
**Depends on:** `none`
**Prerequisites:** None. The focused test passes on the current baseline.
**Files and symbols:** Edit `tests/test_validator.py` / `ValidatorTest.test_names_missing_file` and `validator.py` / `missing_file_error`; no new files or symbols.
**Test:** In `tests/test_validator.py`, change the input to `"settings file.json"` and use `self.assertEqual('missing file: "settings file.json"', missing_file_error("settings file.json"))`. Run `python3 -B -m unittest tests.test_validator` from the repository root before implementation; expect the assertion to fail because the actual diagnostic is unquoted.
**Implementation:** After observing the red test, preserve the function signature and prefix while wrapping the interpolated supplied path in double quotes. Rerun the same test command; expect the exact diagnostic assertion to pass.
**Validate:** From `/Users/chris/multica_workspaces/chris-banes-f4baf65e0996/cb-13-fbf8fb9abafb/workdir/skills/.scratch/skill-evals/cb13-revision4-one-function-20260924/workspaces/to-plan-authorized-draft-direct/forced/1/attempt-1`, run `python3 -B -m unittest tests.test_validator`; expect one test to run and pass after implementation.
**Complete when:** The diagnostic is exactly `missing file: "settings file.json"`, preserving the supplied path including its space inside quotes, and the focused unit test passes.

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| `missing_file_error` preserves a path containing spaces inside quotes after the existing prefix, with its public signature unchanged. | 1 | Exact diagnostic assertion in `ValidatorTest.test_names_missing_file`; focused unittest passes. |

## Final validation

- From the repository root above, run `python3 -B -m unittest tests.test_validator`; expect the focused test suite to pass.
```

Judge summary: The supplied plan meets the local, test-first planning requirements, but misses the rubric’s explicit repair-budget requirement.

## Final disposition

- Two-slice calibration: **FAIL** because `proportionality` fails. The judge found repeated contract detail beyond the brief Approach summary, especially in Guardrails, Planning decisions, both slice descriptions, completion conditions, and acceptance rows. All other six criteria pass.
- One-function counterexample: **FAIL overall**. Its `proportionality` criterion passes, but `executor-readiness` fails because the one-slice plan omits an explicit diagnosis/edit-validation budget. All other three criteria pass.
- Every criterion received a pass or fail; none is unproven. Both plans passed deterministic validation. The two-pair budget is exhausted. No further repair or model calls were made.