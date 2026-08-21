# Repository skill evaluations

This directory contains a reproducible, advisory evaluator with a shared core
and suite-specific catalogs, fixtures, coverage rules, and safety policies. It
tests concrete scenarios modelled on real-world coding work, with expected
outcomes, allowed-write boundaries, and no-change controls. The committed suites
cover six Compose skills plus `gradle-run`, `kotlin-api-design`,
`kotlin-concurrency-and-flow`, and `kotlin-control-flow`. It is designed to
answer two separate questions:

1. Does a skill improve the correctness and restraint of the resulting work?
2. Does automatic activation report the expected public skill entrypoints?

The evaluator never turns a stochastic model score into a merge or release
gate. CI validates only the harness, corpus, and deterministic formulas.

## Results

**Baseline** is the positive-case pass rate with no skills available.
**Automatic** is the positive-case pass rate with every repository skill
available but none named in the prompt. **Restraint** is the no-change-control
pass rate: the skill may inspect the task, but must not make an unnecessary
change. The table reports complete-scenario-suite measurements.

The rows are descriptive diagnostics, not individual release gates. Multi-skill
scenarios contribute to each relevant skill row, so the rows are not a
suite-wide aggregate.

| Skill | Baseline | Automatic | Restraint |
| --- | ---: | ---: | ---: |
| `compose-animations` | 75.0% | 100.0% | 100.0% |
| `compose-component-design` | 86.7% | 100.0% | 100.0% |
| `compose-focus-navigation` | 66.7% | 100.0% | 100.0% |
| `compose-performance` | 91.7% | 100.0% | 100.0% |
| `compose-state-and-effects` | 77.8% | 100.0% | 100.0% |
| `compose-ui-testing-patterns` | 55.6% | 100.0% | 100.0% |
| `gradle-run` | 33.3% | 75.0% | 100.0% |
| `kotlin-api-design` | 66.7% | 91.7% | 100.0% |
| `kotlin-concurrency-and-flow` | 33.3% | 100.0% | 66.7% |
| `kotlin-control-flow` | 27.8% | 77.8% | 100.0% |

### Targeted repair rechecks

Focused rechecks validate repaired scenarios only. They do not replace or
recalculate a full-suite result.

| Skill | Positive records | Automatic | Restraint |
| --- | ---: | ---: | ---: |
| `gradle-run` | 12 | 100.0% | 100.0% |
| `kotlin-api-design` | 12 | 100.0% | 100.0% |
| `kotlin-concurrency-and-flow` | 6 | 100.0% | 100.0% |
| `kotlin-control-flow` | 3 | 100.0% | Not measured |

## Evaluation setup

### Arms

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

### Corpus

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

### Models

The recommended evaluation configuration uses:

- subject: `gpt-5.6-terra` with `medium` reasoning; and
- judge: `gpt-5.6-sol` with `high` reasoning.

The Terra subject avoids the ceiling observed when Sol-medium solved every
calibration case without skills, while the stronger Sol judge keeps outcome
assessment stable.

Keep the pair unchanged across all arms. Use a separate, explicitly named run
for another model or reasoning effort; never combine fingerprints in one
scorecard.

## Running evaluations

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

## Scoring and gates

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
