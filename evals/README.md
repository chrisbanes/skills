# Repository skill evaluations

This directory contains a reproducible, advisory evaluator with a shared core
and suite-specific catalogs, fixtures, coverage rules, and safety policies. The
committed suites cover the six Compose skills and the first expansion cohort:
`gradle-run`, `kotlin-api-design`, `kotlin-concurrency-and-flow`, and
`kotlin-control-flow`. It is designed
to answer two separate questions:

1. Does a skill improve the correctness and restraint of the resulting work?
2. Does automatic activation report the expected public skill entrypoints?

The evaluator never turns a stochastic model score into a merge or release
gate. CI validates only the harness, corpus, and deterministic formulas.

## Latest Compose per-skill scores

The 2026-08-18 certified scorecard produced the following descriptive scores.
**Automatic score** is the positive-case outcome pass rate when all skills and
the router are available without naming a skill in the prompt.
Baseline and forced scores show the same cases with no skills or with the target
skill explicitly invoked. Uplift is forced minus baseline. Restraint is the
outcome pass rate on forced and automatic no-change controls.

| Skill | Positive records per arm | Baseline | Forced | Automatic score | Uplift | Restraint (forced / automatic) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `compose-animations` | 12 | 75.0% | 100.0% | 100.0% | +25.0 pp | 100.0% / 100.0% |
| `compose-component-design` | 15 | 86.7% | 100.0% | 100.0% | +13.3 pp | 100.0% / 100.0% |
| `compose-focus-navigation` | 9 | 66.7% | 100.0% | 100.0% | +33.3 pp | 100.0% / 100.0% |
| `compose-performance` | 24 | 91.7% | 100.0% | 100.0% | +8.3 pp | 100.0% / 100.0% |
| `compose-state-and-effects` | 27 | 77.8% | 100.0% | 100.0% | +22.2 pp | 100.0% / 100.0% |
| `compose-ui-testing-patterns` | 9 | 55.6% | 100.0% | 100.0% | +44.4 pp | 100.0% / 100.0% |

These rows are diagnostic rather than independent pass/fail gates. Multi-skill
routing cases contribute to every expected skill row, so the rows do not sum to
the suite-wide rates. The aggregate certification passed with 82.7% baseline
and 100.0% forced and automatic positive outcomes; 89.4% reported routing
precision; 97.7% reported routing recall; and 100.0% forced and automatic
negative-control restraint.

Provenance: the scorecard retains unaffected conditions from the previous
complete benchmark and uses the latest three-repetition result for every
condition targeted by the finalized skill edits, plus a current safety probe.
The raw historical scorecard retains its two earlier forbidden actions; the
current probe recorded none. See the experiment design and safety rules below
when interpreting the table.

This historical Compose scorecard used the then-current Compose-only automatic
catalog. New runs use the full public repository catalog as described below, so
do not combine old and new fingerprints or present their routing rates as one
condition.

## Latest Kotlin/Gradle per-skill scores

The separate 2026-08-19 run evaluated all 19 Kotlin/Gradle cases with the full
15-skill automatic catalog, three repetitions, Terra medium subjects, and Sol
high blinded judges.

| Skill | Positive records per arm | Baseline | Forced | Automatic score | Uplift | Restraint (forced / automatic) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gradle-run` | 12 | 33.3% | 100.0% | 75.0% | +66.7 pp | 100.0% / 100.0% |
| `kotlin-api-design` | 12 | 66.7% | 100.0% | 91.7% | +33.3 pp | 100.0% / 100.0% |
| `kotlin-concurrency-and-flow` | 12 | 33.3% | 100.0% | 100.0% | +66.7 pp | 66.7% / 66.7% |
| `kotlin-control-flow` | 18 | 27.8% | 83.3% | 77.8% | +55.6 pp | 100.0% / 100.0% |

Aggregate positive outcomes were 44.4% baseline, 93.3% forced, and 84.4%
automatic. Automatic retention was 81.8%; reported automatic routing precision
and recall were 96.3% and 94.0%. Forced and automatic negative-control restraint
were both 91.7%, and one genuine forbidden action remained: an automatic
value-class response edited undeclared `Fixture.kt`.

The run passed forced-uplift, automatic-retention, routing-precision, and
routing-recall gates. It did not pass the negative-control or
zero-forbidden-action gates. Human audit found that
`kotlin-control-exhaustiveness-novel` requires access to an otherwise-unused
error payload while also asking for a behavior-preserving rewrite.

A separately fingerprinted 2026-08-20 follow-up corrected that rubric and
scored 100.0% for none, forced, and automatic arms (3/3 each), with 100.0%
routing precision/recall and no forbidden action, process failure, or retry.
The disabled discoverable-skill catalog changed from 142 to 160 entries between
runs because installed plugin versions changed. The evaluator therefore failed
closed instead of merging the new case records into the frozen 2026-08-19
aggregate. Treat the follow-up as evidence that the earlier case result was a
rubric artifact, not as a recalculated cohort score.

## Experiment arms

Every case runs in a fresh workspace and conversation under three arms:

- `none` disables every discoverable skill.
- `forced` enables and explicitly invokes only the case's target skill or
  skills. Negative controls still force the target so over-application remains
  observable.
- `automatic` enables all 15 public repository skills without naming any skill
  in the task prompt. This measures cross-domain routing interference as well as
  target-skill activation.

Each `case × arm` condition runs three times by default. The 38-case Compose
suite schedules 342 subject calls and 342 blinded judge calls. The 19-case
Kotlin/Gradle suite schedules 171 subject calls and 171 blinded judge calls.

All subject and judge processes use `--ignore-user-config`, explicit
`skills.config` entries, network-disabled sandboxes, disabled hosted web search,
output schemas, and pinned model/reasoning arguments. Review tasks are read-only.
Edit tasks are graded against a path allowlist. Workspaces and conversations are
never reused across conditions.

The harness disables every skill discovered in the user and plugin catalogs.
For forced and automatic arms it copies only the enabled repository skills into
the fresh workspace's project-local `.agents/skills` directory before committing
the fixture baseline. The subject output schema is staged beside the fixture so
the baseline command does not disclose the source checkout or target skill
names. These evaluator-owned files are excluded from the blinded judge packet.

Codex 0.147 does not emit an independent skill-activation event. Routing
precision and recall therefore use the subject's schema-constrained
`skills_used` declaration and are labeled **reported routing**. Plugin-qualified
and local skill identifiers are canonicalized to the same repository skill. They are not
proof that the runtime loaded a particular `SKILL.md`; outcome differences and
the human audit provide the behavioral evidence.

## Corpus

The Compose benchmark remains 38 scored cases and comprises:

- one direct authorized edit, one novel read-only review, and one authorized
  no-change control for each of 11 focused concern slices across the six skills;
- five router reviews spanning single-cluster and multi-skill decisions; and
- one normalized snapshot from an immutable public revision per concern slice,
  with source URL, revision, license, and normalization note in `case.json`.

Case IDs retain their focused concern names even when several concerns route to
the same clustered public skill.

Four calibration-only performance challenge cases are also validated with the
corpus. They are excluded from default plans and published scorecards; select
them explicitly with `--case` when deciding whether they should graduate into
the benchmark.

The Kotlin/Gradle benchmark contains 19 scored cases:

- a direct task, novel review, and no-change restraint control for each of its
  four skills;
- one additional high-risk branch per skill;
- three multi-skill routing cases; and
- three immutable public-source snapshots across API, Flow, and control-flow
  concerns.

Use `--suite compose` or `--suite kotlin-gradle` to select one advisory
scorecard. The default remains `compose` for command compatibility. Never mix
suites into one pass/fail result; repository-wide summaries are descriptive.

`case.json` defines routing expectations, task mode, allowed writes, deterministic
validators, rubric criteria, and provenance. Safety checks for network and external
tools, permission escalation, destructive commands, undeclared writes, and online
Gradle invocations are global evaluator policy. `prompt.md` is the arm-neutral task.
`overlay/` is copied over the fixture selected by the case's suite. The
Kotlin/Gradle fixture presents subjects with a deterministic networkless
`gradlew` simulation while external validators use `gradlew-real` to compile
and test edits with the pinned distribution. Both case and fixture contents are
included in result fingerprints.
`expectations.json` is consumed only by the external deterministic grader and is
not copied into the subject workspace.

No-change controls still expect the relevant domain skill to be consulted. They
measure behavioral restraint through the unchanged-workspace requirement rather
than treating correct inspection as a routing false positive.

Validate the entire contract without model calls:

```shell
npm run evals:validate
npm test
```

## Models

The recommended public scorecard uses:

- subject: `gpt-5.6-terra` with `medium` reasoning; and
- judge: `gpt-5.6-sol` with `high` reasoning.

The Terra subject avoids the ceiling observed when Sol-medium solved every
calibration case without skills, while the stronger Sol judge keeps outcome
assessment stable.

Keep the pair unchanged across all arms. Use a separate, explicitly named run
for another model or reasoning effort; never combine fingerprints in one
scorecard.

## Preview and execute

Preview the complete matrix and call count:

```shell
python3 evals/run.py plan \
  --suite kotlin-gradle \
  --model gpt-5.6-terra --reasoning medium \
  --judge-model gpt-5.6-sol --judge-reasoning high \
  --repetitions 3
```

Pass current, user-verified per-call cost assumptions to include a USD estimate;
the harness deliberately does not bake in a price table that can go stale:

```shell
python3 evals/run.py plan \
  --model gpt-5.6-terra --reasoning medium \
  --judge-model gpt-5.6-sol --judge-reasoning high \
  --subject-cost-per-call-usd <amount> \
  --judge-cost-per-call-usd <amount>
```

`run` is also a preview unless `--execute` is present. Start with a one-case
smoke run after authenticating Codex and warming the pinned Gradle distribution:

```shell
python3 evals/run.py run \
  --suite kotlin-gradle \
  --case kotlin-api-ownership-direct \
  --arm none --arm forced --arm automatic \
  --model gpt-5.6-terra --reasoning medium \
  --judge-model gpt-5.6-sol --judge-reasoning high \
  --subject-cost-per-call-usd <amount> \
  --judge-cost-per-call-usd <amount> \
  --repetitions 1 --execute
```

Use `--skill`, repeated `--case` or `--arm` filters, and `--output-dir` to bound
a run. Raw results are atomic and fingerprinted by the case, arm, skill commit,
Codex version, and both model settings. Reusing the same output directory resumes
matching results and rejects stale fingerprints.
The fingerprint also covers the discovered external skill catalog and the exact
repository skill contents staged into subject workspaces.

Rebuild reports from completed raw records without model calls:

```shell
python3 evals/run.py report --output-dir .scratch/skill-evals/<run-id>
```

If deterministic validators or safety matchers change after a run, reapply only
those local checks without overwriting raw evidence or repeating model calls:

```shell
python3 evals/run.py regrade --output-dir .scratch/skill-evals/<run-id>
```

Regraded results and reports are written under `<run-id>/regraded/`.

Persisted blinded packets can be rejudged without repeating subject calls. The
command previews by default and writes separate fingerprinted rejudgments when
`--execute` is supplied, preserving the original judgment:

```shell
python3 evals/run.py judge \
  --output-dir .scratch/skill-evals/<run-id> \
  --judge-model gpt-5.6-sol --judge-reasoning high
```

After all rejudgments complete, build a separate scorecard that combines those
verdicts with the immutable subject and deterministic-grading evidence:

```shell
python3 evals/run.py rejudged-report \
  --output-dir .scratch/skill-evals/<run-id>
```

This report fails rather than guessing if a packet is missing, has no
rejudgment, or has multiple rejudgments for one packet. Its results, scorecard,
and audit queue are written under `<run-id>/rejudged/`; the original run remains
unchanged.

## Grading and gates

The outcome judge receives an opaque candidate ID, task, rubric, initial source,
final diff, response, and validator evidence. It never receives the arm, skill selection,
routing expectation, raw Codex configuration, or deterministic verdict.

A task outcome passes only when all deterministic validators and required judge
criteria pass. Safety remains an independent result. Each suite's advisory
scorecard applies these gates over the three repetitions:

- forced positive-case pass rate improves on baseline by at least 10 percentage
  points;
- automatic activation retains at least 80% of that uplift, and retention is
  not met when forced uplift is non-positive;
- reported automatic-routing micro precision and recall are each at least 85%;
- forced and automatic no-change controls do not regress below baseline; and
- forbidden-action failures are zero.

Subject and judge tokens, tool calls, elapsed time, process failures, and retries
are diagnostics, not gates. The scorecard also reports how often the router
itself was declared in the automatic arm. Missing arms or case categories are
shown as `not met`; filtered smoke runs cannot pass gates they did not evaluate.

## Human audit

Each run writes `results.json`, `scorecard.md`, and `audit-queue.json`. The audit
queue includes every objective/judge disagreement, every within-condition
inconsistency, and a deterministic 10% sample of remaining results. Human audit
decisions supplement raw judgments; they must not overwrite the original
subject output, validator evidence, or judge response.

Append a decision to the run's JSONL audit ledger:

```shell
python3 evals/run.py audit --output-dir .scratch/skill-evals/<run-id> \
  --id <case:arm:repetition> --decision accept --rationale "Evidence checked"
```
