# GPT-6 evaluation corpus audit

This Phase 1 audit preserves the original Luna/high subject and Sol/high judge
run and repairs only the contradictory or impossible corpus contracts named in
the improvement plan. It does not change a skill or publish a corrected score.

## Results and provenance

The original three-repetition run and its immutable packets are documented in
[the benchmark record](2026-09-23-gpt6-luna-high.md). The original aggregate
results were:

| Suite | Positive baseline | Forced | Automatic |
| --- | ---: | ---: | ---: |
| Compose | 77.8% | 88.9% | 91.4% |
| Kotlin/Gradle | 56.9% | 88.2% | 80.4% |
| Workflows/writing | 0.0% | 27.8% | 38.9% |

Corrected-corpus scores are **pending**. No corrected model run was performed
as part of this corpus-only phase. The revised prompts, fixtures, expectations,
and case manifests change case digests; old subject or judge results must not be
mixed into a corrected scorecard. Run new subject and judge repetitions for all
eligible arms of the ten changed case directories before reporting corrected
scores. The untouched Compose corpus has no corrected result from this phase.

The harness fingerprint combines each case digest, arm, Codex version, skill
SHA and catalog digest, subject model/reasoning, and judge model/reasoning. The
case digest hashes the files under the case directory and its named fixture
(excluding fixture build caches). Thus prompt, fixture, expectation, and
manifest edits require new fingerprints. The raw run remains under the original
fingerprints in `.scratch/skill-evals/2026-09-23-gpt6-*` in the source checkout.

## Audit coverage

The audit queues contained 84 Compose, 55 Kotlin/Gradle, and 94 workflows/
writing entries: 233 total. I inspected every subject/judge record in the
priority cases: 63 records across seven Kotlin direct cases and 24 across the
three workflow cases. Those cases contain 10 and 19 queued entries
respectively; all 29 overlapping queue entries were triaged. I also reviewed
three unique, non-priority queue entries from each suite (nine total). The
remaining **195 of 233 queue entries are unreviewed**.

There were 16 objective/judge disagreements across the priority cases: one in
the Kotlin group and 15 in the workflow group. There were no saved
`forbidden_action_failure` flags in those records. A direct read of the event
traces nevertheless found command attempts in four of six `shepherd-novel`
records and all three forced `android-benchmark-comparison-negative` records;
these cases explicitly prohibited commands. The old configured command matcher
did not mark those read-only shell commands as forbidden. The new
`forbid_all_commands` case property makes any subject `command_execution` event
fail both the objective grade and forbidden-action result.

### Non-priority sample

| Suite | Queue entry | Finding |
| --- | --- | --- |
| Compose | `compose-animations-direct:automatic:2` | Objective checks passed, but the judge rejected a content key that groups all non-null states, since distinct text values then share one key. This is a substantive judgment difference for later skill/case review. |
| Compose | `compose-state-authoring-direct:forced:3` | The deterministic validator failed while the judge accepted the private snapshot state and read-only public getter. The disagreement warrants a separate validator audit. |
| Compose | `compose-ui-testing-patterns-direct:forced:2` | Objective checks and judge both passed; the response used the public default capture option and preserved the existing tolerance. |
| Kotlin/Gradle | `gradle-fingerprint-diagnosis-novel:none:2` | The judge rejected a proposed source repair because the reported source file was absent; it wanted the path discrepancy reconciled before another build. |
| Kotlin/Gradle | `kotlin-api-platform-boundary-novel:none:1` | The judge accepted the proposed common interface but found its explanation omitted lifecycle ownership and runtime-injection rationale. |
| Kotlin/Gradle | `gradle-completed-validation-negative:automatic:3` | Objective and judge passed; the response reused a passing targeted test at the same source digest and made no extra run. |
| Workflows/writing | `android-benchmark-comparison-novel:automatic:1` | Objective checks passed, but the judge found the response omitted reversing run order, inspecting trace intervals, and restoring affinity settings. |
| Workflows/writing | `grounded-writing-direct:automatic:1` | The deterministic text validator and judge both failed: the copy did not give a clear choice between settings and retained implementation details. |
| Workflows/writing | `grounded-writing-negative:none:1` | Objective and judge passed; the response found no concrete issue and left the approved report unchanged. |

## Case decisions

| Case or rule | Original evidence and decision | Corpus correction |
| --- | --- | --- |
| `shepherd-novel` | All six judge records failed the local-boundary criterion because the rubric demanded local checks and the exact macOS check name. The prompt prohibited commands and the supplied state did not name that check. The responses correctly reported the verification boundary; the rubric was impossible as written. Four subject records still attempted shell commands despite the prompt. | Keep this a novel, analysis-only task. It now states the exact information gap, asks for the failed log, diff, and check name before a targeted repair, preserves the no-mutation boundary, and requires no unsupported check claims. `forbid_all_commands` enforces the boundary. |
| `android-benchmark-comparison-direct` | The fixture claimed raw results and traces were attached but contained neither, and it omitted completed-case and iteration counts. Three judge disagreements penalized responses for the absent evidence even when they left the default unresolved and did not invent values. | The fixture now explicitly says raw results, traces, and counts are absent. The prompt and rubric credit that evidence gap, prohibit invented coverage, and keep a bounded decision pending the missing evidence. Deterministic expectations reject explicit benchmark count claims and result fields while allowing ordinary build IDs, issue references, citations, and historical metadata. |
| `android-benchmark-comparison-negative` | The prompt required reading `draft.md` while prohibiting commands, with no alternative file-reading tool. Six judge disagreements came from inability to inspect the file or inconsistent judgments of the incomplete response. All three forced records attempted a `cat` of the skill file. | Supply the exact draft inline and keep the on-disk fixture synchronized. The task now asks for an 80-column check; the unchanged text already passes. The rubric and validator retain no-change behavior and forbid performance experiments. `forbid_all_commands` catches shell attempts. |
| `kotlin-api-ownership-direct` | No objective/judge disagreement occurred, but the validator rejected every retained `String.loadProfile` shim. The reference contract says to preserve or deprecate a public entry point unless a breaking change is explicitly authorized. One forced response removed the API and passed the old validator; automatic responses and two forced responses preserved/deprecated it and failed. This rewarded a possibly breaking API change. | The prompt now explicitly requires a deprecated, source-compatible forwarding shim. Structural expectations accept ordinary multiline signatures and either a member or extension owner method, require a typed collaborator and owner-method calls from the shim and caller, and reject direct repository access through a different receiver. Focused examples cover `ProfileStore` and `ProfileRepository` forms. |
| Kotlin direct-case routing | Across seven Kotlin edit cases, 20 of 21 automatic records did not execute Gradle, yet all 21 were expected to report `gradle-run`. One record, `kotlin-control-exhaustiveness-direct:automatic:2`, invoked the runner for compile and test. Searches for `gradlew` were not executions. | Each target skill is now required, and `gradle-run` is an allowed optional skill. Automatic results add it to the expected set only when subject events contain a real Gradle or `gradle_run.py run` invocation. Filename searches do not count. The dedicated Gradle routing cases remain intact. |

The unrelated sampled mismatch `kotlin-control-guards-direct:none:3` remains a
known deterministic false negative: its valid `when (val classified = event)`
guard uses `classified.isUnread`, while the validator insists on
`event.isUnread`; the judge accepted the alias. It is outside the Phase 1 case
list and is left for the follow-up skill/validator phase.

## Verification

The revised corpus retains its direct, novel, and no-change/negative coverage.
Validation completed:

- `python3.13 evals/run.py validate` — 99 cases validated.
- `python3.13 -m unittest discover -s evals/tests -p 'test_*.py'` — 196 tests
  passed.
- `python3.13 -m unittest scripts/test_release.py skills/run-github-project/scripts/test_rank_tickets.py skills/gradle-run/scripts/test_gradle_run.py skills/release-kotlin-library/scripts/test_release.py` — 171 tests passed, one skipped.
- `npm run lint` and remark on this artifact — passed. This isolated checkout
  had no `node_modules`, so lint temporarily linked the existing dependency
  tree and removed that link afterward.

The default npm test/validation wrappers selected Xcode Python 3.9, which
cannot import this repository's `datetime.UTC` dependency. The full equivalent
test suites and corpus validation passed when invoked directly with Python
3.13. No model score is inferred from deterministic checks; corrected results
remain pending the fresh run described above.
