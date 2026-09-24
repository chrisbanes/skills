# GPT-6 Luna/high skill improvement follow-up

This follow-up applies a measurement-first repair plan against `gpt-6-luna` at
high reasoning, judged by `gpt-6-sol` at high
reasoning. The [original run](2026-09-23-gpt6-luna-high.md) remains intact.
The [corpus audit](2026-09-23-gpt6-corpus-audit.md) records every case-contract
change and the original packet decisions.
The [score evidence ledger](2026-09-24-gpt6-score-evidence.jsonl) preserves
case, arm, repetition, fingerprints, run controls, and pass/fail fields for the
selected frozen suites and the focused runs cited here and in the later repair
records. It omits full model transcripts and workspace diffs. The ledger lets
readers inspect outcome accounting after local raw directories expire, but it
does not support an independent qualitative rejudgment.

The plan first audited objective/judge disagreements and impossible case
contracts, then changed only skill decisions supported by the traces. It
required direct, novel, no-change, routing, and safety checks before claiming
an improvement. A uniform three-suite rerun produced the frozen scorecards
below; later user-authorized work used focused checks only. The later focused
repairs and their remaining limits are recorded in the
[inline repair record](2026-09-24-gpt6-inline-repair-results.md).

### Intermediate alternate-CLI checks

The following focused runs used the ChatGPT-bundled Codex CLI
`0.155.0-alpha.16` after the installed CLI stalled at its version preflight.
They used `gpt-6-luna/high` as subject and `gpt-6-sol/high` as judge. Each
row preserves its original raw result and source revision; different rows
must not be combined into one suite score.
The raw directories are machine-local and are not included in this repository;
the committed tables and audit decisions do not permit a full replay after
those directories are removed.

| Case and revision | Forced | Automatic | Raw output |
| --- | ---: | ---: | --- |
| Compose state hoisting direct, `0aa790e` | 3/3 | 3/3 | `/private/tmp/gpt6-compose-state-hoisting-alt-cli-3rep` |
| Compose focus navigation novel, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-compose-focus-novel-alt-cli-3rep` |
| Compose recomposition performance novel, `2114de7` | 2/3 | Not run | `/private/tmp/gpt6-compose-remaining-forced-alt-cli-3rep` |
| Compose state authoring novel, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-compose-remaining-forced-alt-cli-3rep` |
| Compose state authoring novel, `ee3584e` | Not run | 3/3 | `/private/tmp/gpt6-compose-state-authoring-auto-alt-cli-3rep` |
| Compose animation/focus/testing overlap, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-compose-remaining-forced-alt-cli-3rep` |
| Kotlin Flow state/events novel, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-kotlin-flow-concurrency-alt-cli-3rep` |
| Kotlin concurrency router, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-kotlin-flow-concurrency-alt-cli-3rep` |
| Kotlin concurrency router, `ee3584e` | Not run | 2/3 | `/private/tmp/gpt6-kotlin-concurrency-router-auto-alt-cli-3rep` |
| Gradle incidental validation direct, `6f62dd7` | 3/3 | 3/3 | `/private/tmp/gpt6-gradle-incidental-alt-cli-3rep` |
| Kotlin API ownership direct, `6f62dd7` | Not run | 3/3 | `/private/tmp/gpt6-kotlin-api-ownership-auto-alt-cli-3rep` |
| Shepherd novel, `0aa790e` | 3/3 | Ineligible | `/private/tmp/gpt6-shepherd-novel-alt-cli-3rep` |
| Implement with subagents direct, novel, and no-change, `53ddfc9` | 9/9 | Ineligible | `/private/tmp/gpt6-implement-subagents-alt-cli-3rep` |
| Release direct, `0aa790e` | 2/3 | 2/3 | `/private/tmp/gpt6-release-direct-alt-cli-3rep` |
| Grounded writing direct, `ab748e1` | 3/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Grounded writing novel, `ab748e1` | 1/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Grounded writing no-change, `ab748e1` | 3/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Release direct after ledger-order repair, `15415a2` | 3/3 | 2/3 | `/private/tmp/gpt6-release-direct-ledger-alt-cli-3rep` |
| Grounded writing direct after shared-contract repair, `15415a2` | Not run | 3/3 | `/private/tmp/gpt6-writing-direct-contract-alt-cli-3rep` |
| Android benchmark direct, `c65d99d` | Not run | 1/3 raw | `/private/tmp/gpt6-benchmark-direct-auto-alt-cli-3rep` |

These probes exposed the preview-tooling scope miss, an unmeasured Compose
performance rewrite, a smart-cast routing omission, a release approval-handoff
miss, and writing restraint failures. The benchmark direct automatic probe
also exposed an objective matcher disagreement and judge false negatives about
an edited file. Later repairs and fresh outcomes are documented in the inline
repair record; no failed raw packet was relabelled as a pass.

## Measurement and skill changes

The corpus audit triaged all 29 queue entries in the priority cases and sampled
nine other entries. The remaining 195 of 233 original queue entries are
unreviewed. The revised corpus keeps 99 validated cases, including direct,
novel, and no-change coverage. It repairs contradictory instructions or
unavailable evidence in `shepherd-novel`, the benchmark cases, and
`kotlin-api-ownership-direct`; Kotlin direct cases now expect `gradle-run` only
when Gradle actually runs. The screenshot-review novel rubric credits a
finding that the named artifact and baseline diff are absent. The original
scorecard was not overwritten.

Skills now make the observed decisions more explicit: literal screenshot
artifact and diff evidence; Kotlin branch payload and independent second-skill
routing; reader-facing setting guidance; a direct planning question and
confirmed summary; joined-head dependency checks; benchmark reversal and
affinity restoration; and the Compose build-file edit boundary. An independent
review found one conflicting exception in `grounded-writing`; the original
owner corrected it before integration. No plugin version changed.

The evaluator now permits a forced arm to read only its exact target skill
entrypoint in two analysis-only cases, while still rejecting task-file reads
and other commands. It excludes generated `.kotlin` compiler caches from
fixture copies, Git diffs, and case digests. The first two Kotlin final-run
shards were quarantined because preflight generated this cache before the fix;
their packets are excluded from all results below.

## Paired targeted evidence

These comparisons use the same case digest, subject and judge models,
reasoning, and Codex CLI. Old and revised instruction runs remain separate;
the counts are small and do not replace the full scorecard. A pass requires
both the objective checks and the judge.

| Case group | Old skill | Revised skill | Interpretation |
| --- | ---: | ---: | --- |
| `compose-ui-testing-patterns-novel`, forced | 3/3 | 3/3 | The corrected rubric accounts for much of the original failure; no forced-arm gain is established. |
| `compose-ui-testing-patterns-novel`, automatic | 1/3 | 2/3 | Directional improvement in this small sample. |
| `router-kotlin-api-control`, forced and automatic | 0/3 each | 1/3 each | Smart-cast payload advice remains inconsistent. |
| `implement-with-subagents` direct and novel, forced | 0/2 | 2/2 | Both joined-head and overlap decisions passed in the probe. |
| `to-plan` direct and novel, forced | 0/2 | 1/2 | The direct case still omitted the future confirmation gate. |
| `grounded-writing` direct and novel, forced | 0/2 | 2/2 | Reader-facing public copy passed in the probe. |
| `grounded-writing` direct and novel, automatic | 0/2 | 2/2 | Automatic skill use passed in the probe. |

The repaired `android-benchmark-comparison-negative` case passed all three
arms in the old-skill three-repetition run, with zero forbidden actions and
valid forced evidence. The revised one-repetition benchmark probe passed both
positive forced cases and its no-change control, with zero forbidden actions.
The screenshot and benchmark case repairs are measurement corrections as well
as skill tests; gains from a corrected rubric are not attributed to skill text.

The targeted benchmark direct probe exposed two further judge/objective
disagreements. In the no-skill arm, the edited comparison said the reported
improved consistency could not be quantified and the raw results and traces
were not included. The judge accepted it, while the text matcher missed both
equivalent phrases. A narrow deterministic correction at `b85fce1` accepts
them; the saved response passes the corrected validator. In the automatic arm,
the subject diff contained a valid `comparison.md` edit, but the judge claimed
it could not write under a read-only sandbox and rejected the result. That
claim conflicts with the captured diff and is an audited judge false negative;
the raw judgment remains unchanged.

The unchanged `shepherd` skill passed 2/3 forced runs before the skill edits
and 3/3 afterward on the repaired prompt, so a one-run difference is not by
itself evidence of a skill effect. Both runs had valid forced evidence and no
forbidden actions.

Across 39 completed revised targeted records, 16 objective/judge results
disagreed and none had a forbidden-action flag. The two benchmark disagreements
above are measurement errors. The other disagreements reflect substantive
omissions in the saved replies, chiefly smart-cast advice, planning
confirmation, and joined-head acceptance in no-skill arms. They are not
silently counted as passes.

## Final frozen-corpus run

The final run contains 81 scored cases. Each eligible case/arm condition had
three repetitions: 342 Compose, 198 Kotlin/Gradle, and 153 workflow/writing
records (693 subject records and 693
judge verdicts). The subject and judge were `gpt-6-luna/high` and
`gpt-6-sol/high`, using Codex CLI `0.155.1`. Selected records have zero
process failures and retries. Every selected forced record has valid target
preflight, observed invocation, and skill reporting.

| Suite | No-skill positive | Forced positive | Automatic positive | No-change restraint | Gates |
| --- | ---: | ---: | ---: | --- | --- |
| [Compose](2026-09-24-gpt6-compose-scorecard.md) | 79.0% | 91.4% | 95.1% | 100% in both skill arms | All pass |
| [Kotlin/Gradle](2026-09-24-gpt6-kotlin-gradle-scorecard.md) | 51.0% | 90.2% | 86.3% | 100% in both skill arms | All pass |
| [Workflows/writing](2026-09-24-gpt6-workflows-scorecard.md) | 11.1% | 50.0% | 61.1% | Forced 100%; automatic 88.9% | Forbidden actions fail |

The [Compose](2026-09-24-gpt6-compose-merge-manifest.json),
[Kotlin/Gradle](2026-09-24-gpt6-kotlin-gradle-merge-manifest.json), and
[workflow](2026-09-24-gpt6-workflows-merge-manifest.json) merge manifests
record selected shard paths, fingerprints, catalog digests, and case reruns.
Raw packets remain in the local run directories named there.

Kotlin/Gradle automatic retention was 90.0% and routing recall was 98.7%,
above the plan's 80% and 85% thresholds. The only selected forbidden action
was the `grounded-writing-negative:automatic:1` report edit described below.
The selected workflow run has no forced-integrity failures after a complete
rerun of `android-benchmark-comparison-negative`. The selected Kotlin run
likewise uses a complete rerun of `router-kotlin-concurrency-control`; its
original forced record combined two target reads with a semicolon and failed
the standalone-read integrity check. The rerun's single `cat` command read
both target files, and the captured output hash matches their staged bytes
concatenated in operand order. Both original invalid packets remain in their
raw runs, and no single repetition was cherry-picked.

The frozen skill source is commit `6f03744`. The Kotlin cache-exclusion harness
fix at `bf43d59` was used while pointing at the same frozen skill and case
source. Compose and Kotlin records use catalog digest `57bc4ee9…` (173
paths); workflow records use `c2901452…` (153 paths). An external plugin
cache gained 20 disabled templates while the run was in progress. We discarded
the earlier Compose packets and reran all affected cases under the pinned
173-path catalog, so each selected suite is internally consistent. No
cross-suite skill effect is inferred from the different catalog digests.

The corrected deterministic evaluator at `edef6aa` accepts benchmark
uncertainty phrasing and the `2.0.1-SNAPSHOT` heading permitted by the release
prompt. At `a3f79fd`, it accepts a private `MutableState` backing value with
a public read-only getter. Saved model packets were regraded without changing
raw replies or judge verdicts. [Compose audit decisions](2026-09-24-gpt6-compose-audit-decisions.jsonl),
[Kotlin/Gradle audit decisions](2026-09-24-gpt6-kotlin-gradle-audit-decisions.jsonl),
and [workflow audit decisions](2026-09-24-gpt6-workflows-audit-decisions.jsonl)
record all 107 final-run objective/judge disagreement dispositions. Four
workflow and three Kotlin objective-pass replies are supported judge false
negatives, but the published scorecard retains their raw judgments. Detailed
per-skill correctness and subject-side efficiency are in the three linked
scorecards.

## Post-freeze writing restraint repair

The frozen workflow run found a real no-change failure in
`grounded-writing-negative:automatic:1`: the subject edited an approved
internal report to add an unverified `([model])` placeholder to the device
matrix. The judge passed the reply, but the file diff violated the case's
no-change boundary. The raw record is retained as a failure.

Revision `7569a8d` now tells the writing skill to leave an adequate draft
unchanged when the request permits edits only for material clarity or truth
problems. A separate three-repetition probe of the direct, novel, and
no-change writing cases produced 5/6 forced and 4/6 automatic positive passes,
3/3 no-change passes in each skill-enabled arm, no forbidden actions, valid
forced evidence, and 100% automatic routing precision and recall. This probe
has no no-skill arm and is not spliced into the frozen suite scorecard. Its
[scorecard](2026-09-24-gpt6-writing-repair-scorecard.md)
and raw packets remain separate. The first sandboxed attempt failed before any
model calls and is excluded.

## Remaining limits

The human audit queue is incomplete: the priority 29 entries and nine sampled
entries from the original queue were reviewed, while 195 of 233 original
entries remain. The final-run disagreement decisions do not constitute a full
audit of the remaining sample queue. The corrected corpus also changes some
case contracts, so full-suite percentages cannot be treated as a causal
old-versus-new skill comparison. The paired targeted runs above are smaller
but use identical case digests.

`to-plan` still has only 66.7% forced no-change restraint and 50.0% forced
positive passes. Kotlin smart-cast advice remains inconsistent in router
cases. `android-benchmark-comparison` forced positive passes are 16.7%, below
its 33.3% no-skill rate in this three-repetition corpus. The frozen workflow
suite's forbidden-action gate failed. The later writing repair passed its
no-change probe but has not been rerun across the whole workflow suite.
