# Claude Code results: Haiku 5.5 / high, judged by Sonnet 5.5 / high

This record is the evidence behind the Claude Code tables in
[`README.md`](../../README.md) and [`evals/README.md`](../README.md). It reports
one full run of each committed suite and is advisory, not a release gate. It
replaces the [2026-10-17 record](2026-10-17-claude-haiku-5-5-results.md).

## Configuration

- Subject: `claude-haiku-5-5`, high effort, Claude Code 2.1.302 (`claude -p`).
- Judge: `claude-sonnet-5-5`, high effort, Claude Code 2.1.302. The previous
  record used `gpt-6.1-sol` on Codex, which was too slow; judge-dependent
  numbers are therefore not directly comparable with that record.
- Arms: `none`, `forced`, `automatic`; three repetitions per eligible
  condition. Calls: compose 342 subject + 342 judge, kotlin-gradle 216 + 216,
  workflows-writing 264 + 264. Corpus: 212 validated cases.
- Skills and harness: the repository at `b0d941a` (`main` after #129).
- Cost assumptions were passed as `0` USD per call because the Claude login
  has no per-call price; the scorecards' cost estimates are placeholders.
- Isolation: unchanged from the previous record. The scorecards report 0
  invalid forced-evidence, missing-target, invocation-failure and
  reporting-failure records.

## Table rules

Baseline and Automatic are the positive-case pass rates over cases eligible for
automatic activation and are `—` when the scorecard reports Automatic as
"not met" (explicit-only skills). Restraint is the forced-arm no-change pass
rate, falling back to the automatic arm only when forced is "not met".

## Run integrity

- Process failures: compose 1, kotlin-gradle 1, workflows-writing 0. Each was
  a single subject attempt that succeeded on the automatic retry (compose and
  kotlin-gradle 2 retries each, workflows-writing 0). No judge call retried.
- Forbidden-action gate: NOT MET in all three suites (compose 19, kotlin-gradle
  14, workflows-writing 5 failing records). By arm (none, forced, automatic):
  compose 7, 2, 10; kotlin-gradle 9, 1, 4; workflows-writing 3, 2, 0. About
  half occur with skills disabled, so they mostly reflect model habit rather
  than skill behavior. Compose: Gradle commands without `--offline` and
  undeclared test or build-file writes. Kotlin-gradle: commands run despite an
  analysis-only boundary and undeclared test writes. Workflows-writing: `gh`
  calls in `shepherd-negative`, whose prompt has since been tightened; this run
  used the earlier prompt.
- Regrade: the scorecards were regraded without new model calls after one rule
  change. The harness now treats `gradle-run` as expected in every automatic
  case where Gradle ran, not only in cases that list it. Compose routing
  precision moved from 76.6% to 93.0% reported (74.5% to 92.4% observed) and
  now passes. Compose routing recall moved from 88.4% to 82.8% reported (79.8%
  to 76.3% observed) and is NOT MET, because the subject sometimes ran Gradle
  without activating `gradle-run`. Outcome pass rates and the README tables
  are unchanged. Kotlin-gradle and workflows-writing routing gates pass.

## Known failures

Positive-case failures outside the no-skill arm:

- Automatic: `compose-state-authoring-novel` (1),
  `gradle-fingerprint-diagnosis-novel` (2), `kotlin-api-value-class-direct`
  (1), `router-kotlin-gradle-validation` (1).
- Forced: `kotlin-api-value-class-direct` (1), `deliver-spec-novel` (2).

Every other failing record is in the `none` arm, where skills are disabled.

## Scorecards

### Compose

> This experiment is not a merge or release gate.

#### Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | 88.9% | 100.0% |
| forced | 100.0% | 100.0% |
| automatic | 98.8% | 100.0% |

#### Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compose-animations` | 12 | 91.7% | 100.0% | 100.0% | 8.3% | 100.0% | 100.0% |
| `compose-component-design` | 15 | 86.7% | 100.0% | 100.0% | 13.3% | 100.0% | 100.0% |
| `compose-focus-navigation` | 9 | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 100.0% |
| `compose-performance` | 24 | 91.7% | 100.0% | 100.0% | 8.3% | 100.0% | 100.0% |
| `compose-state-and-effects` | 24 | 79.2% | 100.0% | 95.8% | 20.8% | 100.0% | 100.0% |
| `compose-ui-testing-patterns` | 9 | 88.9% | 100.0% | 100.0% | 11.1% | 100.0% | 100.0% |

#### Effect and routing

- Forced uplift: 11.1%
- Automatic retention: 88.9%
- Reported automatic routing precision: 93.0%
- Reported automatic routing recall: 82.8%
- Observed routing precision: 92.4%
- Observed routing recall: 76.3%
- Router reported in automatic arm: 2.6%
- Forbidden-action failures: 19
- Forbidden-action failures by arm: none 7, forced 2, automatic 10

#### Evaluator integrity

- Invalid forced evidence: 0
- missing target: 0
- invocation failure: 0
- reporting failure: 0

#### Efficiency (non-gating)

Subject-only metrics. Medians describe a typical run, including any retry. Per-pass totals include failed runs, so a quick incorrect result is not rewarded.

| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 105 / 114 | 73.8k | 7 | 1 | 35.9s | 154.7k | 10.5 | 1.1 | 52.4s |
| forced | 114 / 114 | 82.5k | 7 | 1 | 29.8s | 101.8k | 7.6 | 1 | 32.2s |
| automatic | 113 / 114 | 96.8k | 8 | 1 | 42.8s | 139.3k | 9.4 | 1.0 | 47.0s |

#### Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `compose-animations` | 51.8k → 85.9k (+66%) | 6 → 8 (+33%) | 1 → 1 (+0%) | 47.7s → 46.4s (-3%) |
| `compose-component-design` | 52.2k → 72.8k (+40%) | 6 → 6 (+0%) | 1 → 1 (+0%) | 30.2s → 35.2s (+16%) |
| `compose-focus-navigation` | 62.2k → 88.9k (+43%) | 7.5 → 8 (+7%) | 1 → 1 (+0%) | 44.6s → 56.9s (+27%) |
| `compose-performance` | 94.3k → 103.8k (+10%) | 8 → 9 (+12%) | 1 → 1 (+0%) | 45.0s → 51.3s (+14%) |
| `compose-state-and-effects` | 72.4k → 118.4k (+64%) | 7 → 9 (+29%) | 1 → 1 (+0%) | 39.4s → 51.3s (+30%) |
| `compose-ui-testing-patterns` | 87.0k → 88.3k (+2%) | 10 → 8 (-20%) | 1 → 1 (+0%) | 39.3s → 44.7s (+13%) |

Claude Code token counts are input, cache creation, cache read, and output tokens; its tool calls exclude the structured-output call. Wall-clock time is environment-sensitive.

#### Evaluation diagnostics (non-gating)

- Input tokens: 46472051
- Output tokens: 2616660
- Tool events: 3378
- Elapsed time: 17244.5s
- Process failures: 1
- Retries: 2

#### Gates

- forced_integrity: PASS
- forced_uplift: PASS
- automatic_retention: PASS
- routing_precision: PASS
- routing_recall: NOT MET
- negative_controls: PASS
- forbidden_actions: NOT MET

### Kotlin and Gradle

> This experiment is not a merge or release gate.

#### Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | 57.9% | 93.3% |
| forced | 98.2% | 100.0% |
| automatic | 93.0% | 100.0% |

#### Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gradle-run` | 18 | 16.7% | 100.0% | 83.3% | 83.3% | 100.0% | 100.0% |
| `kotlin-api-design` | 12 | 91.7% | 91.7% | 91.7% | 0.0% | 100.0% | 100.0% |
| `kotlin-concurrency-and-flow` | 18 | 72.2% | 100.0% | 100.0% | 27.8% | 100.0% | 100.0% |
| `kotlin-control-flow` | 18 | 61.1% | 100.0% | 94.4% | 38.9% | 100.0% | 100.0% |

#### Effect and routing

- Forced uplift: 40.4%
- Automatic retention: 87.0%
- Reported automatic routing precision: 100.0%
- Reported automatic routing recall: 92.2%
- Observed routing precision: 98.9%
- Observed routing recall: 86.3%
- Router reported in automatic arm: 0.0%
- Forbidden-action failures: 14
- Forbidden-action failures by arm: none 9, forced 1, automatic 4

#### Evaluator integrity

- Invalid forced evidence: 0
- missing target: 0
- invocation failure: 0
- reporting failure: 0

#### Efficiency (non-gating)

Subject-only metrics. Medians describe a typical run, including any retry. Per-pass totals include failed runs, so a quick incorrect result is not rewarded.

| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 47 / 72 | 88.2k | 8 | 1 | 38.2s | 203.4k | 14.2 | 1.6 | 74.2s |
| forced | 71 / 72 | 90.6k | 7 | 1 | 31.0s | 116.8k | 7.4 | 1.0 | 34.7s |
| automatic | 68 / 72 | 127.9k | 9 | 1 | 38.9s | 166.7k | 9.2 | 1.1 | 47.1s |

#### Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `gradle-run` | 75.6k → 105.6k (+40%) | 6 → 5 (-17%) | 1 → 1 (+0%) | 36.3s → 29.9s (-18%) |
| `kotlin-api-design` | 96.7k → 101.8k (+5%) | 8 → 9 (+12%) | 1 → 1 (+0%) | 45.4s → 53.5s (+18%) |
| `kotlin-concurrency-and-flow` | 111.2k → 145.2k (+31%) | 9.5 → 10 (+5%) | 1 → 1 (+0%) | 47.1s → 50.4s (+7%) |
| `kotlin-control-flow` | 119.5k → 138.1k (+16%) | 10 → 10 (+0%) | 1 → 1 (+0%) | 41.3s → 44.1s (+7%) |

Claude Code token counts are input, cache creation, cache read, and output tokens; its tool calls exclude the structured-output call. Wall-clock time is environment-sensitive.

#### Evaluation diagnostics (non-gating)

- Input tokens: 31144605
- Output tokens: 1685679
- Tool events: 2030
- Elapsed time: 11125.2s
- Process failures: 1
- Retries: 2

#### Gates

- forced_integrity: PASS
- forced_uplift: PASS
- automatic_retention: PASS
- routing_precision: PASS
- routing_recall: PASS
- negative_controls: PASS
- forbidden_actions: NOT MET

### Workflows and writing

> This experiment is not a merge or release gate.

#### Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | 16.7% | 75.0% |
| forced | 100.0% | 100.0% |
| automatic | 100.0% | 100.0% |

#### Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `android-benchmark-comparison` | 6 | 33.3% | 100.0% | 100.0% | 66.7% | 100.0% | 100.0% |
| `deliver-spec` | 6 | 0.0% | 66.7% | not met | 66.7% | 100.0% | not met |
| `grounded-writing` | 6 | 0.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `implement-with-subagents` | 6 | 33.3% | 100.0% | not met | 66.7% | 100.0% | not met |
| `release-kotlin-library` | 6 | 16.7% | 100.0% | 100.0% | 83.3% | 100.0% | 100.0% |
| `run-github-project` | 33 | 51.5% | 100.0% | not met | 48.5% | 100.0% | not met |
| `shepherd` | 6 | 0.0% | 100.0% | not met | 100.0% | 100.0% | not met |
| `to-plan` | 6 | 16.7% | 100.0% | 100.0% | 83.3% | 100.0% | 100.0% |

#### Effect and routing

- Forced uplift: 83.3%
- Automatic retention: 100.0%
- Reported automatic routing precision: 100.0%
- Reported automatic routing recall: 90.9%
- Observed routing precision: 96.8%
- Observed routing recall: 90.9%
- Router reported in automatic arm: 0.0%
- Forbidden-action failures: 5
- Forbidden-action failures by arm: none 3, forced 2, automatic 0

#### Evaluator integrity

- Invalid forced evidence: 0
- missing target: 0
- invocation failure: 0
- reporting failure: 0

#### Efficiency (non-gating)

Subject-only metrics. Medians describe a typical run, including any retry. Per-pass totals include failed runs, so a quick incorrect result is not rewarded.

| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 13 / 36 | 36.1k | 3 | 1 | 20.5s | 113.4k | 8.5 | 2.8 | 64.5s |
| forced | 36 / 36 | 56.6k | 3 | 1 | 23.5s | 64.1k | 3.4 | 1 | 27.2s |
| automatic | 36 / 36 | 62.5k | 4 | 1 | 27.6s | 73.9k | 4.2 | 1 | 31.6s |

#### Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `android-benchmark-comparison` | 37.7k → 66.3k (+76%) | 3 → 3 (+0%) | 1 → 1 (+0%) | 22.0s → 22.6s (+3%) |
| `grounded-writing` | 46.6k → 73.6k (+58%) | 3 → 5 (+67%) | 1 → 1 (+0%) | 19.2s → 28.3s (+47%) |
| `release-kotlin-library` | 55.5k → 60.7k (+9%) | 5 → 3 (-40%) | 1 → 1 (+0%) | 43.6s → 54.9s (+26%) |
| `to-plan` | 22.9k → 53.4k (+133%) | 2 → 4 (+100%) | 1 → 1 (+0%) | 9.4s → 21.8s (+132%) |

Claude Code token counts are input, cache creation, cache read, and output tokens; its tool calls exclude the structured-output call. Wall-clock time is environment-sensitive.

#### Evaluation diagnostics (non-gating)

- Input tokens: 15011751
- Output tokens: 1548981
- Tool events: 1001
- Elapsed time: 9710.3s
- Process failures: 0
- Retries: 0

#### Gates

- forced_integrity: PASS
- forced_uplift: PASS
- automatic_retention: PASS
- routing_precision: PASS
- routing_recall: PASS
- negative_controls: PASS
- forbidden_actions: NOT MET
