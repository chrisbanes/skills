# CB-13 slice-boundary calibration: plan and judge evidence

This artifact preserves the generated plan and full criterion-level judge
rationale for the approved revision 2 calibration run.

## Run controls and deterministic evidence

- Run against branch `agent/big-head/fbf8fb9abafb`, starting HEAD
  `b282da46383312309ebb790f2d1dfc088f35b6f3`; the slice-boundary changes
  were present as working-tree edits in the isolated subject workspace.
- Subject: `gpt-6-luna` / high; judge: `gpt-6-sol` / high; Codex CLI
  `codex-cli 0.155.1`; one forced repetition.
- Budget used: one subject call and one judge call. No retries, invalid run,
  or additional pair was needed.
- Case digest: `792ff68864e74e0cc5b1d1d80eba829e5304e4fcdf655d594df69810ae62e966`.
- Run fingerprint: `1e580d4c8d29d87118c4bd257996eda312017747f5195d6e3417983d6d9d466b`.
- Raw `results.json` SHA-256: `1537bbf95e95062f75f90d4e562a83f4cc8c9ff02fe85703bb80d51c8fa5242c`.
- Validator passed: `validated to-plan-specificity-calibration`.
- Subject violations: none.
- Before model execution, both baseline overlay tests passed against the
  unquoted implementations. The prior grouped plan was rejected by the new
  deterministic check because both behaviors shared T1; a synthetic plan with
  separate slices passed the same check.
- Before model execution: `python3.13 evals/run.py validate --suite
  workflows-writing` passed (38 cases); `python3.13 -m unittest
  evals.tests.test_workflows_writing_matrix` passed (27 tests);
  `npm run lint` and `git diff --check` passed.

## Judge result

**Overall: PASS.** The supplied plan covers both requested diagnostic changes with accurate, independent test-first steps and exact acceptance checks. The supplied diff stays within the planning boundary.

| Criterion | Result | Judge evidence |
| --- | --- | --- |
| `complete-coverage` | PASS | The acceptance table maps both diagnostics to their own slice and exact focused test. |
| `baseline-and-red-green` | PASS | The plan identifies both current unquoted assertions, specifies the exact quoted replacements, and requires each changed assertion to fail before its formatter is edited and pass afterward. |
| `independent-slice-boundaries` | PASS | T1 covers missing_manifest_error and its test; T2 covers invalid_profile_error and its test. Both declare no dependencies. |
| `concrete-tests` | PASS | The file, function, and test names match the repository snapshot. Both slices specify the spaced-path input, exact expected output, repository-root command, and passing result. |
| `consistent-dependencies` | PASS | T1 and T2 have explicit, empty dependency lists. The acceptance rows match their respective slices and verification commands; the graph is acyclic. |
| `proportionality` | PASS | The plan uses two small independent slices for the two call sites and includes the fixture-required validator command. |
| `planning-boundary` | PASS | The supplied diff adds one local plan and shows no source or test edits. The supplied response reports no provider contact. |

## Generated plan

```markdown
<!-- to-plan:conversation-plan:v1 id=21a8f9d8-9a5f-4116-9c17-c345d2b58b3b -->

# Quote Paths in Diagnostic Errors

**Planned against:** `main` at `2d48b53e4e32aa058287a21e223e001f3b9b5082`
**Local state:** Clean

## Approach

Update each diagnostic formatter to put a single quote immediately before and after its supplied path, preserving the existing prefix and path text. Update and run each function's existing focused unit test independently.

## Guardrails

- Preserve the public signatures `missing_manifest_error(path: str) -> str` and `invalid_profile_error(path: str) -> str`.
- Preserve prefixes `manifest not found: ` and `invalid profile at `, and preserve the supplied path verbatim between the surrounding single quotes, including spaces such as in `configs/team manifest.json`.
- Do not change validator behavior or unrelated diagnostics.

## Planning decisions

- Keep the two changes in separate slices. Each formatter has its own existing test module and can be implemented and verified independently; there is no cross-call dependency.
- Use exact-string assertions for the quoted diagnostic so the test proves both the unchanged prefix and the path, including its embedded space.

## Implementation context

- **Existing:** `manifest_reader.py` — `missing_manifest_error(path)` currently returns `manifest not found: {path}`.
- **Existing:** `tests/test_manifest_reader.py` — `ManifestReaderTest.test_quotes_missing_manifest_path` calls the formatter with `configs/team manifest.json` and currently asserts the unquoted string.
- **Existing:** `profile_loader.py` — `invalid_profile_error(path)` currently returns `invalid profile at {path}`.
- **Existing:** `tests/test_profile_loader.py` — `ProfileLoaderTest.test_quotes_invalid_profile_path` calls the formatter with `configs/team manifest.json` and currently asserts the unquoted string.

## Implementation slices

**Task graph and parallelism:** The graph is acyclic. T1 and T2 are independent and may run concurrently: each owns a different source file and test file, and each focused test verifies its own formatter. No shared-file or integration constraint exists.

### 1. Quote missing-manifest paths

**Task ID:** `T1`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Edit existing `tests/test_manifest_reader.py`, `ManifestReaderTest.test_quotes_missing_manifest_path`, and `manifest_reader.py`, `missing_manifest_error(path)`. No new files or symbols.
**Test:** First change the exact expected string for input `configs/team manifest.json` to `manifest not found: 'configs/team manifest.json'`, keeping the existing formatter call. Run `python3 -B -m unittest tests.test_manifest_reader` from the repository root before changing the formatter; expect the assertion to fail because the current result has no quotes. After implementation, the same test must pass and match the complete string exactly.
**Implementation:** After the test-first failure, change only the formatter's returned string to surround `{path}` with single quote characters. Keep its signature and `manifest not found: ` prefix unchanged; do not transform, trim, escape, or otherwise alter the supplied path.
**Validate:** From the repository root, after the assertion update and formatter edit, run `python3 -B -m unittest tests.test_manifest_reader`; expect the module's test to pass.
**Complete when:** The formatter returns `manifest not found: 'configs/team manifest.json'` for the existing spaced-path input and its focused test passes.

### 2. Quote invalid-profile paths

**Task ID:** `T2`
**Depends on:** `none`
**Prerequisites:** None.
**Files and symbols:** Edit existing `tests/test_profile_loader.py`, `ProfileLoaderTest.test_quotes_invalid_profile_path`, and `profile_loader.py`, `invalid_profile_error(path)`. No new files or symbols.
**Test:** First change the exact expected string for input `configs/team manifest.json` to `invalid profile at 'configs/team manifest.json'`, keeping the existing formatter call. Run `python3 -B -m unittest tests.test_profile_loader` from the repository root before changing the formatter; expect the assertion to fail because the current result has no quotes. After implementation, the same test must pass and match the complete string exactly.
**Implementation:** After the test-first failure, change only the formatter's returned string to surround `{path}` with single quote characters. Keep its signature and `invalid profile at ` prefix unchanged; do not transform, trim, escape, or otherwise alter the supplied path.
**Validate:** From the repository root, after the assertion update and formatter edit, run `python3 -B -m unittest tests.test_profile_loader`; expect the module's test to pass.
**Complete when:** The formatter returns `invalid profile at 'configs/team manifest.json'` for the existing spaced-path input and its focused test passes.

## Acceptance coverage

| Acceptance criterion | Slice | Verification |
| --- | ---: | --- |
| `missing_manifest_error` encloses the unchanged supplied path in single quotes and preserves its prefix and spaced path text. | 1 | `python3 -B -m unittest tests.test_manifest_reader` passes with an exact assertion for `manifest not found: 'configs/team manifest.json'`. |
| `invalid_profile_error` encloses the unchanged supplied path in single quotes and preserves its prefix and spaced path text. | 2 | `python3 -B -m unittest tests.test_profile_loader` passes with an exact assertion for `invalid profile at 'configs/team manifest.json'`. |

## Final validation

- From the repository root, after both slices are complete, run `python3 -B -m unittest tests.test_validator`; expect the validator test to pass. This is the repository fixture's required final validation command; the focused slice commands above verify the changed formatters.

## Review focus

- Confirm the only diagnostic text change is a pair of single quote delimiters around each supplied path, and that exact tests retain the embedded space and unchanged prefixes.

## Allowed deviations

- Within the fixed contract, only mechanical test or fixture corrections may be made after one focused diagnosis pass and at most two repair edit-and-validation cycles across unexpected mismatches; report any repair.

## Re-plan triggers

- Stop if preserving the public signatures, prefixes, or supplied path text requires a contract change, if the implementation baseline changes in either formatter or its test, or if a mismatch remains after the repair budget. Report the evidence, attempted repair and validation, and remaining decision or upstream change; do not invoke `to-plan` from the implementation worktree.
```

## Limits

This is one forced observation of one synthetic scenario. It supports the
slice-boundary behavior for this case version; it does not establish
repeatability, automatic routing, or production behavior. The approved extra
pair was unused because the first pair was valid and passed the stated
acceptance criteria.
