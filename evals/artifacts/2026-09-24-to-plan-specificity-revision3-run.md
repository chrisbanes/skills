# CB-13 revision 3 proportionality calibration evidence

This record preserves both generated plans and every criterion-level judge
rationale from the two approved subject/judge pairs.

## Deterministic prechecks

- The prior 126-line plan is rejected by the revised proportionality
  expectation because it includes generic deviation and re-plan sections.
- A concise synthetic two-slice plan with exact files, test commands, and
  acceptance mapping passes the same validator.
- The grouped-slice regression still rejects two independent call sites in
  one task; fixture baseline, prompt neutrality, rubric and dependency
  checks pass.
- Before model calls: 28 workflow matrix tests, 38-case corpus validation,
  `npm run lint`, and `git diff --check` passed.

## Pair 1: initial revision 3 run

- Subject/judge: `gpt-6-luna` / high; `gpt-6-sol` / high; one forced repetition.
- Case digest: `0651cd30f7696684ac196f4a018b6b2209f336701eae7e12acd9ea954b4304fb`; fingerprint: `86a9292bcdef2c3990b959e928c87e062c9c880164359f67a36ff4d9dfc3aca4`.
- Deterministic validator: PASS (validated to-plan-specificity-calibration).
- Judge overall: **FAIL**. The plan covers both behaviors with independent, testable slices, but repeats the shared contract enough to miss the rubric’s proportionality requirement.

| Criterion | Result | Judge rationale |
| --- | --- | --- |
| `complete-coverage` | PASS | The acceptance table covers both diagnostics and links each to its implementation slice and focused test. |
| `baseline-and-red-green` | PASS | Both existing assertions expect unquoted output. Each slice changes its assertion first, expects a failure, then changes the formatter and expects a pass. |
| `independent-slice-boundaries` | PASS | T1 and T2 cover separate call sites and tests, each with no dependency. |
| `concrete-tests` | PASS | The slices name the files, symbols, test methods, spaced-path input, exact expected strings, repository-root commands, and expected passing results. |
| `consistent-dependencies` | PASS | T1 and T2 have explicit 'none' dependencies; acceptance rows refer to their matching numbered slices and tests. The graph is acyclic. |
| `proportionality` | FAIL | The shared quote, prefix, signature, and path-preservation contract is restated across Approach, Guardrails, Planning decisions, both slices, and Review focus, rather than stated once. |
| `planning-boundary` | PASS | The supplied workspace diff adds one plan under .scratch/to-plan/ and shows no source or test edits. No provider contact is shown. |

### Generated plan

```markdown
<!-- to-plan:conversation-plan:v1 id=a5c5bbc3-050b-4c07-8b5a-36e76df3ecfa -->

# Quote paths in manifest and profile diagnostics

**Planned against:** `main` at `0a48798a0d2a51bae51afdf717c4b57dc6abf728`
**Local state:** Clean

## Approach

Update each diagnostic formatter to put a single quote immediately before and after the supplied path. Preserve the existing prefix, function signature, and path text verbatim, including spaces. Update each function's existing unit test to assert the exact quoted message.

## Guardrails

- Keep `missing_manifest_error(path: str) -> str` and `invalid_profile_error(path: str) -> str` signatures unchanged.
- Preserve the exact prefixes `manifest not found: ` and `invalid profile at ` and preserve the supplied path contents; for example, `configs/team manifest.json` remains intact inside the quotes.
- Limit changes to these two diagnostics and their focused tests. Do not alter other diagnostics such as `validator.missing_file_error`.

## Planning decisions

- Handle the call sites as separate increments. Each function has its own existing test and can be verified without the other; they touch distinct source and test files, so no intermediate state is untestable.
- Add literal single-quote delimiters around the interpolated path without normalizing, splitting, or otherwise transforming it. This realizes the requested formatting while preserving path text.

## Implementation context

- **Existing:** `manifest_reader.py` — `missing_manifest_error(path)` returns `manifest not found: ` followed by the supplied path; its focused caller contract is asserted in `tests/test_manifest_reader.py`.
- **Existing:** `profile_loader.py` — `invalid_profile_error(path)` returns `invalid profile at ` followed by the supplied path; its focused caller contract is asserted in `tests/test_profile_loader.py`.

## Implementation slices

**Task graph and parallelism:** The graph has two independent root tasks and is acyclic. T1 and T2 may run concurrently because each edits a separate implementation file and its corresponding separate test file; neither consumes the other's changes.

### 1. Quote paths in missing-manifest diagnostics

**Task ID:** `T1`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Edit existing `tests/test_manifest_reader.py`, `ManifestReaderTest.test_quotes_missing_manifest_path`, to assert the requested exact string. Edit existing `manifest_reader.py`, `missing_manifest_error(path: str) -> str`, to produce that string while keeping its public signature.
**Test:** In `tests/test_manifest_reader.py`, call `missing_manifest_error("configs/team manifest.json")` and assert equality with `"manifest not found: 'configs/team manifest.json'"`. The test-first red result is an assertion failure against the current unquoted output.
**Implementation:** First change the expected assertion to include a single quote immediately after `manifest not found: ` and after the unchanged `configs/team manifest.json`. Then change only the formatter in `missing_manifest_error` to add those delimiters around the interpolated path. Retain the prefix and the `path: str` parameter and return type.
**Validate:** From the repository root, after no setup, run `python3 -B -m unittest tests.test_manifest_reader`; expect the focused test to pass with `OK` and the exact output assertion above.
**Complete when:** `missing_manifest_error` returns `manifest not found: 'configs/team manifest.json'` for the example input and its focused test passes.

### 2. Quote paths in invalid-profile diagnostics

**Task ID:** `T2`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Edit existing `tests/test_profile_loader.py`, `ProfileLoaderTest.test_quotes_invalid_profile_path`, to assert the requested exact string. Edit existing `profile_loader.py`, `invalid_profile_error(path: str) -> str`, to produce that string while keeping its public signature.
**Test:** In `tests/test_profile_loader.py`, call `invalid_profile_error("configs/team manifest.json")` and assert equality with `"invalid profile at 'configs/team manifest.json'"`. The test-first red result is an assertion failure against the current unquoted output.
**Implementation:** First change the expected assertion to include a single quote immediately after `invalid profile at ` and after the unchanged `configs/team manifest.json`. Then change only the formatter in `invalid_profile_error` to add those delimiters around the interpolated path. Retain the prefix and the `path: str` parameter and return type.
**Validate:** From the repository root, after no setup, run `python3 -B -m unittest tests.test_profile_loader`; expect the focused test to pass with `OK` and the exact output assertion above.
**Complete when:** `invalid_profile_error` returns `invalid profile at 'configs/team manifest.json'` for the example input and its focused test passes.

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| Missing-manifest diagnostics preserve their prefix and path text while enclosing the path in single quotes. | 1 | `tests.test_manifest_reader` asserts the exact message for the path containing a space. |
| Invalid-profile diagnostics preserve their prefix and path text while enclosing the path in single quotes. | 2 | `tests.test_profile_loader` asserts the exact message for the path containing a space. |

## Final validation

- From the repository root, after no setup, run `python3 -B -m unittest tests.test_manifest_reader tests.test_profile_loader`; expect both focused suites to pass with `OK`.
- From the repository root, after no setup, run `python3 -B -m unittest tests.test_validator` as required by `AGENTS.md`; expect the validator suite to pass with `OK`.

## Review focus

- Confirm each output keeps its original prefix exactly and places the unchanged, space-containing path between single quotes.
```

## Pair 2: targeted repair

- Subject/judge: `gpt-6-luna` / high; `gpt-6-sol` / high; one forced repetition.
- Case digest: `cdb51c905a34f5c5e89095bdd5c97a8dee0a3d3416d8d54318fc7671ed500f9a`; fingerprint: `9e475fce8f515eb54dfae1533340528914020c71a5b3019f78df21b2e9b085df`.
- Deterministic validator: PASS (validated to-plan-specificity-calibration).
- Judge overall: **FAIL**. The plan covers both independent behaviors with concrete red-green checks. It misses the rubric's proportionality requirement because Approach repeats the shared contract.

| Criterion | Result | Judge rationale |
| --- | --- | --- |
| `complete-coverage` | PASS | The acceptance table maps both diagnostics to their own slice and focused test. |
| `baseline-and-red-green` | PASS | The plan identifies both current unquoted expectations and directs each slice to change its assertion, see it fail against the unchanged helper, then confirm it passes after the edit. |
| `independent-slice-boundaries` | PASS | T1 covers missing_manifest_error and T2 covers invalid_profile_error; each has separate files, a test, and no dependency on the other. |
| `concrete-tests` | PASS | Both slices name the files, functions, test methods, spaced-path input, exact expected output, repository-root working directory, focused unittest command, and expected passing result. |
| `consistent-dependencies` | PASS | T1 and T2 are stable IDs with explicit 'Depends on: none' entries. Acceptance rows point to the corresponding tests and tasks; the graph is acyclic. |
| `proportionality` | FAIL | The Approach repeats the shared single-quote formatting rule that the rubric requires stating once in Guardrails. |
| `planning-boundary` | PASS | The recorded diff adds one plan under .scratch/to-plan/ and shows no source or test edits. The record shows no provider contact. |

### Generated plan

```markdown
<!-- to-plan:conversation-plan:v1 id=67a77eaa-129f-4b07-addf-c06edc231b36 -->

# Quote paths in diagnostic messages

**Planned against:** `main` at `30491e7ae882cc6953180192e36caddf820993de`
**Local state:** Clean

## Approach

Add single quotes around the supplied path in each diagnostic, then update each function's focused unittest expectation to assert the exact result for `configs/team manifest.json`.

## Guardrails

- Preserve each diagnostic prefix, public function signature, and path text exactly; only add the enclosing single quotes.
- Keep the embedded space in `configs/team manifest.json` inside the quotes.
- Do not expand the change beyond these two diagnostic helpers and their focused tests.

## Planning decisions

- Use the existing per-function unittest modules as independent implementation slices: each already calls its corresponding public helper with the path containing a space and asserts the complete diagnostic string.
- Make each slice test-first by changing its expected string to the quoted form before changing the helper; the existing assertion then fails against the current unquoted output and passes after the implementation edit.

## Implementation context

- **Existing:** `manifest_reader.py` — `missing_manifest_error(path: str) -> str` currently returns `manifest not found: {path}`; its caller-facing output is asserted in `tests/test_manifest_reader.py`.
- **Existing:** `profile_loader.py` — `invalid_profile_error(path: str) -> str` currently returns `invalid profile at {path}`; its caller-facing output is asserted in `tests/test_profile_loader.py`.
- **Follow:** `tests/test_manifest_reader.py:ManifestReaderTest.test_quotes_missing_manifest_path` and `tests/test_profile_loader.py:ProfileLoaderTest.test_quotes_invalid_profile_path` for the established exact-string assertion seam and space-containing input.

## Implementation slices

**Task graph and parallelism:** The graph is acyclic: T1 and T2 are independent root tasks (`Depends on: none`). They touch separate source and test files and have focused checks that do not depend on the other slice, so they may run concurrently.

### 1. Quote the missing-manifest path

**Task ID:** `T1`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Edit `tests/test_manifest_reader.py:ManifestReaderTest.test_quotes_missing_manifest_path` and `manifest_reader.py:missing_manifest_error(path: str) -> str`; no new files or symbols.
**Test:** In `tests/test_manifest_reader.py`, call `missing_manifest_error("configs/team manifest.json")` and assert the exact string is `manifest not found: 'configs/team manifest.json'`. First update the assertion while the helper remains unchanged; it must fail because the current output lacks quotes. Then implement the behavior and confirm the same assertion passes.
**Implementation:** First update the existing expected string to `manifest not found: 'configs/team manifest.json'`. Then change only the returned diagnostic formatting in `missing_manifest_error` to enclose the interpolated path in single quotes. Keep the prefix `manifest not found: `, the signature, and the supplied path text unchanged.
**Validate:** From the repository root, after no setup, run `python3 -B -m unittest tests.test_manifest_reader`; expect the focused test to pass and the exact path with its space to appear between single quotes after the unchanged prefix.
**Complete when:** The existing focused test asserts and receives the exact quoted diagnostic, with the function signature and prefix unchanged.

### 2. Quote the invalid-profile path

**Task ID:** `T2`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Edit `tests/test_profile_loader.py:ProfileLoaderTest.test_quotes_invalid_profile_path` and `profile_loader.py:invalid_profile_error(path: str) -> str`; no new files or symbols.
**Test:** In `tests/test_profile_loader.py`, call `invalid_profile_error("configs/team manifest.json")` and assert the exact string is `invalid profile at 'configs/team manifest.json'`. First update the assertion while the helper remains unchanged; it must fail because the current output lacks quotes. Then implement the behavior and confirm the same assertion passes.
**Implementation:** First update the existing expected string to `invalid profile at 'configs/team manifest.json'`. Then change only the returned diagnostic formatting in `invalid_profile_error` to enclose the interpolated path in single quotes. Keep the prefix `invalid profile at `, the signature, and the supplied path text unchanged.
**Validate:** From the repository root, after no setup, run `python3 -B -m unittest tests.test_profile_loader`; expect the focused test to pass and the exact path with its space to appear between single quotes after the unchanged prefix.
**Complete when:** The existing focused test asserts and receives the exact quoted diagnostic, with the function signature and prefix unchanged.

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| Missing-manifest diagnostics enclose the unchanged path in single quotes and preserve the prefix, signature, and embedded space. | 1 | `ManifestReaderTest.test_quotes_missing_manifest_path` via the focused unittest command in T1. |
| Invalid-profile diagnostics enclose the unchanged path in single quotes and preserve the prefix, signature, and embedded space. | 2 | `ProfileLoaderTest.test_quotes_invalid_profile_path` via the focused unittest command in T2. |

## Final validation

- From the repository root, after no setup, run `python3 -B -m unittest tests.test_validator`; expect the validator suite to complete successfully, as required by `AGENTS.md`.
- Run both focused commands from T1 and T2; expect both exact-string assertions to pass.
```

## Limits and disposition

- Both runs pass deterministic validation and six of seven judge criteria.
  In both runs, `proportionality` fails. Pair 1 repeats the shared contract
  across Approach, Guardrails, decisions, slices, and Review focus. Pair 2
  is shorter (65 lines versus 68), but Approach still repeats the quote rule
  already stated in Guardrails.
- All criteria have judge dispositions; none is unproven. The approved
  two-pair subject/judge budget is exhausted, with no retries or further
  calls. No claim of a successful proportionality calibration is made.
- The existing one-function counterexample evidence remains intact in
  `evals/artifacts/2026-09-24-to-plan-specificity-reviewable-run.md` and
  `evals/artifacts/2026-09-24-to-plan-specificity-focused-run.md`; it was
  not re-run in this two-pair targeted calibration. Its historical
  proportionality result is PASS, but its behavior under the revision 3
  wording remains **unproven**.
- This is synthetic evidence from two forced observations; it does not
  establish repeatability, automatic routing, or production behavior.
