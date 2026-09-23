# GPT-6 evaluation corpus audit

This audit preserves the original Luna/high subject and Sol/high judge run,
records the Phase 1 corpus corrections, and documents the Phase 3 measurement
repairs. It does not change a skill or publish a corrected score.

## Results and provenance

The original three-repetition run and its immutable packets are documented in
[the benchmark record](2026-09-23-gpt6-luna-high.md). The original aggregate
results were:

| Suite | Positive baseline | Forced | Automatic |
| --- | ---: | ---: | ---: |
| Compose | 77.8% | 88.9% | 91.4% |
| Kotlin/Gradle | 56.9% | 88.2% | 80.4% |
| Workflows/writing | 0.0% | 27.8% | 38.9% |

Corrected-corpus scores are **pending**. No model calls were made for this
Phase 3 repair. Earlier Phase 1 prompt and fixture changes still require new
outputs where those inputs changed. The three Phase 3 fixes below change only
expectations or a rubric, so their saved packets can be reprocessed under the
new case digests as described below; keep original aggregate scores immutable.
The remaining unchanged Compose cases have no corrected result from this phase.

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
the original prompts explicitly prohibited commands. The old configured
command matcher did not mark those read-only shell commands as forbidden. The
analysis-only grader now rejects commands except for one standalone `cat` of
the case's exact target `.agents/skills/<target>/SKILL.md` entrypoint in a
forced arm, needed for forced-skill evidence. Automatic and no-skill arms still
reject that command. Task-file reads, compound commands, other utilities, and
reads of another skill's entrypoint fail both the objective grade and
forbidden-action result.

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
| `compose-ui-testing-patterns-novel` | The prompt asked for findings only. The saved response inspected `build/recorded/subject.png`, found it absent, and found no baseline diff, while the rubric still required recommending those inspections. That criterion demanded work already completed and conflicted with the requested response. | Grade the finding that the baseline update is unsupported because the recorded image and baseline diff are absent. Keep the findings-only request and tolerance boundary; do not require another inspection recommendation. |
| `shepherd-novel` | All six judge records failed the local-boundary criterion because the rubric demanded local checks and the exact macOS check name. The supplied state did not name that check. The responses correctly reported the verification boundary; the rubric was impossible as written. Four subject records read the skill entrypoint despite the original prompt's absolute prohibition. | Keep this a novel, analysis-only task. It now states the exact information gap, asks for the failed log, diff, and check name before a targeted repair, preserves the no-mutation boundary, and requires no unsupported check claims. The prompt permits one standalone `cat` of the target `SKILL.md` only when forced-skill evidence is required; the grader rejects task-file reads and all other commands. |
| `android-benchmark-comparison-direct` | The fixture claimed raw results and traces were attached but contained neither, and it omitted completed-case and iteration counts. Three judge disagreements penalized responses for the absent evidence even when they left the default unresolved and did not invent values. A saved answer also said per-run spread was unavailable and the judge accepted it, but the deterministic validator only recognized `variab`. | The fixture now explicitly says raw results, traces, and counts are absent. The prompt and rubric credit that evidence gap, prohibit invented coverage, and keep a bounded decision pending the missing evidence. Expectations accept variability or spread language, retain the missing-data guard, reject explicit benchmark count claims, and allow ordinary build IDs, issue references, citations, and historical metadata. |
| `android-benchmark-comparison-negative` | The prompt required reading `draft.md` while prohibiting commands, with no alternative file-reading tool. Six judge disagreements came from inability to inspect the file or inconsistent judgments of the incomplete response. All three forced records read the skill file. The later 80-column validator used `(?m)^.{81,}$`; under `re.DOTALL` it could span lines and reject the unchanged 74-column draft. | Supply the exact draft inline and keep the on-disk fixture synchronized. The width guard now excludes `\r` and `\n`, and tests cover the unchanged multiline draft and exact 80/81-column boundaries. The prompt says the inline text needs no file read, and permits a standalone `cat` of the target `SKILL.md` only for required forced-skill evidence. The grader rejects `cat draft.md`, compound commands, and all other commands, including in the automatic no-skill arm. The rubric and validator retain no-change behavior and forbid performance experiments. |
| `kotlin-api-ownership-direct` | No objective/judge disagreement occurred, but the validator rejected every retained `String.loadProfile` shim. The reference contract says to preserve or deprecate a public entry point unless a breaking change is explicitly authorized. One forced response removed the API and passed the old validator; automatic responses and two forced responses preserved/deprecated it and failed. This rewarded a possibly breaking API change. | The prompt now explicitly requires a deprecated, source-compatible forwarding shim. Structural expectations accept ordinary multiline signatures and either a member or extension owner method, require a typed collaborator and owner-method calls from the shim and caller, and reject direct repository access through a different receiver. Focused examples cover `ProfileStore` and `ProfileRepository` forms. |
| Kotlin direct-case routing | Across seven Kotlin edit cases, 20 of 21 automatic records did not execute Gradle, yet all 21 were expected to report `gradle-run`. One record, `kotlin-control-exhaustiveness-direct:automatic:2`, invoked the runner for compile and test. Searches for `gradlew` were not executions. | Each target skill is now required, and `gradle-run` is an allowed optional skill. Automatic results add it to the expected set only when subject events contain a real Gradle or `gradle_run.py run` invocation. Filename searches do not count. The dedicated Gradle routing cases remain intact. |

### Phase 3 saved-packet regrade boundary

The three Phase 3 measurement repairs change expectations or rubric text, not
prompts or fixtures. Regrade the saved subject text for the benchmark direct
and negative cases with the corrected deterministic expectations; their judge
decisions do not need another call. Rejudge the saved Compose subject response
together with its action trace under the revised rubric, which recognizes the
path inspection, missing artifact, and absent baseline diff already recorded.
Those saved packets may be reprocessed if they retain the relevant response and
events. If a packet lacks them, rerun only that affected arm.

The follow-up command-boundary correction changes the prompts for
`shepherd-novel` and `android-benchmark-comparison-negative`: each now explicitly
permits a standalone `cat` of its target `SKILL.md` entrypoint only for explicit
forced-skill evidence. Because those prompt inputs changed, fresh subject outputs are
required for corrected-run scores on both cases. The old packets can support
the audit of the prior run, but regrading them does not produce results for the
new prompt digests. Record reprocessed results under updated case digests; do
not rewrite the original scorecard or mix original grades with corrected-run
results. No regrade, rejudge, or model run was performed in this repair.

The unrelated sampled mismatch `kotlin-control-guards-direct:none:3` remains a
known deterministic false negative: its valid `when (val classified = event)`
guard uses `classified.isUnread`, while the validator insists on
`event.isUnread`; the judge accepted the alias. It is outside the Phase 1 case
list and is left for the follow-up skill/validator phase.

## Verification

Phase 1 full verification at `b34f9317bbf472f8c7504f714236187c292eaf0e`:

- `python3.13 evals/run.py validate` — 99 cases validated.
- `python3.13 -m unittest discover -s evals/tests -p 'test_*.py'` — 196 tests
  passed.
- `python3.13 -m unittest scripts/test_release.py skills/run-github-project/scripts/test_rank_tickets.py skills/gradle-run/scripts/test_gradle_run.py skills/release-kotlin-library/scripts/test_release.py` — 171 tests passed, one skipped.
- `npm run lint` and remark on this artifact — passed. This isolated checkout
  had no `node_modules`, so lint temporarily linked the existing dependency
  tree and removed that link afterward.

Phase 3 follow-up verification:

```sh
/opt/homebrew/bin/python3.13 -m unittest \
  evals.tests.test_workflows_writing_matrix.WorkflowsWritingMatrixTest.test_formatting_negative_supplies_the_text_and_preserves_the_noop \
  evals.tests.test_workflows_writing_matrix.WorkflowsWritingMatrixTest.test_benchmark_direct_accepts_spread_for_unavailable_variability \
  evals.tests.test_compose_matrix.ComposeMatrixTest.test_ui_testing_novel_grades_findings_without_recommending_reinspection
```

The command ran three tests and passed. These cover spread/unavailable evidence,
per-line 80/81-column boundaries, and the findings-only Compose rubric.

The analysis-only exception and its positive and negative command cases are
covered by `evals.tests.test_grade.DeterministicGradeTest.test_analysis_only_case_allows_only_target_skill_entrypoint_read`;
the existing `test_analysis_only_case_rejects_read_only_command_execution`
continues to reject other read-only task-file commands.

```sh
/opt/homebrew/bin/python3.13 -m unittest \
  evals.tests.test_grade.DeterministicGradeTest \
  evals.tests.test_workflows_writing_matrix.WorkflowsWritingMatrixTest.test_formatting_negative_supplies_the_text_and_preserves_the_noop \
  evals.tests.test_workflows_writing_matrix.WorkflowsWritingMatrixTest.test_benchmark_direct_accepts_spread_for_unavailable_variability \
  evals.tests.test_compose_matrix.ComposeMatrixTest.test_ui_testing_novel_grades_findings_without_recommending_reinspection
```

This ran 45 tests and passed. The corpus validator reported 99 cases; Python
compilation and `git diff --check` passed. I also replayed repetition 1 of the
saved forced `shepherd-novel` and `android-benchmark-comparison-negative`
records through `grade_subject`, omitting case validators to isolate the
command-boundary check. Both traces contain two standalone reads of their exact
target `SKILL.md`; neither is marked forbidden. The synthetic automatic-arm
case confirms the same read remains forbidden there. No model calls or full
packet regrades were performed, and no saved output was modified.

- `python3.13 evals/run.py validate` — 99 cases validated.
- JSON parsing and `git diff --check` — passed.
- `npm run lint` and remark on this artifact — passed.

The full test command uses Python 3.13 because the default npm wrappers select
Xcode Python 3.9, which cannot import this repository's `datetime.UTC`
dependency. Phase 3 did not rerun the full suite or invoke subject/judge models.
The frozen results still need the saved-packet regrade/rejudge described above;
no model score is inferred from deterministic checks.
