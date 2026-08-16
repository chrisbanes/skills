# Compose skill evaluations

This directory contains a reproducible, advisory evaluator for the repository's
11 Compose skills and the `using-chrisbanes-skills` routing layer. It is designed
to answer two separate questions:

1. Does a skill improve the correctness and restraint of the resulting work?
2. Does automatic activation report the expected leaf skills?

The evaluator never turns a stochastic model score into a merge or release
gate. CI validates only the harness, corpus, and deterministic formulas.

## Experiment arms

Every case runs in a fresh workspace and conversation under three arms:

- `none` disables all 11 leaf skills and the router.
- `forced` enables and explicitly invokes only the case's target skill or
  skills. Negative controls still force the target so over-application remains
  observable.
- `automatic` enables all leaf skills and the router without naming any skill
  in the task prompt.

Each `case × arm` condition runs three times by default. The complete corpus
therefore schedules 342 subject calls and 342 blinded judge calls, or 684 calls
in total.

All subject and judge processes use `--ignore-user-config`, explicit
`skills.config` entries, network-disabled sandboxes, output schemas, and pinned
model/reasoning arguments. Review tasks are read-only. Edit tasks are graded
against a path allowlist. Workspaces and conversations are never reused across
conditions.

Codex 0.147 does not emit an independent skill-activation event. Routing
precision and recall therefore use the subject's schema-constrained
`skills_used` declaration and are labeled **reported routing**. They are not
proof that the runtime loaded a particular `SKILL.md`; outcome differences and
the human audit provide the behavioral evidence.

## Corpus

The 38 cases comprise:

- one direct authorized edit, one novel read-only review, and one authorized
  no-change control for each Compose skill;
- five multi-label router-overlap reviews; and
- one normalized snapshot from an immutable public revision per skill, with
  source URL, revision, license, and normalization note in `case.json`.

`case.json` defines routing expectations, task mode, allowed writes, deterministic
validators, rubric criteria, safety rules, and provenance. `prompt.md` is the
arm-neutral task. `overlay/` is copied over the pinned Compose/JVM fixture.
`expectations.json` is consumed only by the external deterministic grader and is
not copied into the subject workspace.

Validate the entire contract without model calls:

```shell
npm run evals:validate
npm test
```

## Models

The recommended public scorecard uses:

- subject: `gpt-5.6-sol` with `medium` reasoning; and
- judge: `gpt-5.6-sol` with `high` reasoning.

Keep the pair unchanged across all arms. Use a separate, explicitly named run
for another model or reasoning effort; never combine fingerprints in one
scorecard.

## Preview and execute

Preview the complete matrix and call count:

```shell
python3 evals/run.py plan \
  --model gpt-5.6-sol --reasoning medium \
  --judge-model gpt-5.6-sol --judge-reasoning high \
  --repetitions 3
```

Pass current, user-verified per-call cost assumptions to include a USD estimate;
the harness deliberately does not bake in a price table that can go stale:

```shell
python3 evals/run.py plan \
  --model gpt-5.6-sol --reasoning medium \
  --judge-model gpt-5.6-sol --judge-reasoning high \
  --subject-cost-per-call-usd <amount> \
  --judge-cost-per-call-usd <amount>
```

`run` is also a preview unless `--execute` is present. Start with a one-case
smoke run after authenticating Codex and warming the pinned Gradle distribution:

```shell
python3 evals/run.py run \
  --case compose-state-authoring-direct \
  --arm none --arm forced --arm automatic \
  --model gpt-5.6-sol --reasoning medium \
  --judge-model gpt-5.6-sol --judge-reasoning high \
  --subject-cost-per-call-usd <amount> \
  --judge-cost-per-call-usd <amount> \
  --repetitions 1 --execute
```

Use `--skill`, repeated `--case` or `--arm` filters, and `--output-dir` to bound
a run. Raw results are atomic and fingerprinted by the case, arm, skill commit,
Codex version, and both model settings. Reusing the same output directory resumes
matching results and rejects stale fingerprints.

Rebuild reports from completed raw records without model calls:

```shell
python3 evals/run.py report --output-dir .scratch/skill-evals/<run-id>
```

Persisted blinded packets can be rejudged without repeating subject calls. The
command previews by default and writes separate fingerprinted rejudgments when
`--execute` is supplied, preserving the original judgment:

```shell
python3 evals/run.py judge \
  --output-dir .scratch/skill-evals/<run-id> \
  --judge-model gpt-5.6-sol --judge-reasoning high
```

## Grading and gates

The outcome judge receives an opaque candidate ID, task, rubric, initial source,
final diff, response, and validator evidence. It never receives the arm, skill selection,
routing expectation, raw Codex configuration, or deterministic verdict.

A task outcome passes only when all deterministic validators and required judge
criteria pass. Safety remains an independent result. The advisory scorecard
applies these gates over the three repetitions:

- forced positive-case pass rate improves on baseline by at least 10 percentage
  points;
- automatic activation retains at least 80% of that uplift, and retention is
  not met when forced uplift is non-positive;
- reported automatic-routing micro precision and recall are each at least 85%;
- forced and automatic no-change controls do not regress below baseline; and
- forbidden-action failures are zero.

Tokens, tool calls, elapsed time, process failures, and retries are diagnostics,
not gates. The scorecard also reports how often the router itself was declared
in the automatic arm. Missing arms or case categories are shown as `not met`;
filtered smoke runs cannot pass gates they did not evaluate.

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
