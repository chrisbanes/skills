# Claude Code results: Haiku 5.5 / high, judged by GPT-6.1 Sol / high

This record is the evidence behind the Claude Code tables in
[`README.md`](../../README.md) and [`evals/README.md`](../README.md). It reports
one full run of each committed suite and is advisory, not a release gate.

## Configuration

- Subject: `claude-haiku-5-5`, high effort, Claude Code 2.1.299 (`claude -p`).
- Judge: `gpt-6.1-sol`, high reasoning, Codex 0.162.1.
- Arms: `none`, `forced`, `automatic`; three repetitions per eligible
  condition. Calls: compose 342 subject + 342 judge, kotlin-gradle 216 + 216,
  workflows-writing 264 + 264. Corpus: 206 validated cases.
- Skills and harness: the tree of the pull request that adds this file, after
  the skill edits and Claude harness changes it describes. Codex prompts are
  unchanged by those harness changes (a pinned-hash test guards this).
- Isolation: subjects cannot read `~/.claude`, `~/.agents` or the source
  checkout (Read rule and sandbox `denyRead`); skills are staged as plain files
  in the workspace.

## Table rules

Baseline and Automatic are the positive-case pass rates over cases eligible for
automatic activation and are `—` when the scorecard reports Automatic as
"not met" (explicit-only skills). Restraint is the forced-arm no-change pass
rate, falling back to the automatic arm only when forced is "not met".

## Run integrity

- Process failures: compose 0, kotlin-gradle 1, workflows-writing 1. Both
  failures were single no-skill subject runs that succeeded on the automatic
  retry. No judge call timed out in these runs.
- Scorecards below were regraded with the current deterministic grader without
  new model calls. Pass rates and per-skill tables were identical to the
  originals; only the forbidden-action counts moved (compose 19 to 15,
  kotlin-gradle 20 to 19, workflows-writing unchanged at 1). The destructive
  command check no longer parses `rm` operands: a recursive `rm` is a violation
  only when the sandbox blocked it (permission-style error) or its outcome is
  unknown, because a removal that succeeded stayed inside what the sandbox
  allows and any workspace damage already appears in the diff checks. `git
  reset --hard`, `git clean`, `git push`, `sudo` and merge commands remain
  unconditional violations. Most earlier hits were the subject deleting its own
  scratch directories while compiling by hand.
- The staged cross-skill reference for `run-github-project-unattended-direct`
  was also visible to the no-skill arm in this run. That case is explicit-only,
  so no Baseline or Automatic cell depends on it. The harness now stages the
  file only when the consuming skill is enabled.
- Observed routing counts a successful `Skill` call, a whole-file `Read` of this
  run's own staged `SKILL.md`, or a plain `cat` of it (a sibling attempt's copy
  does not count). The scorecards keep the observed
  values stored when the runs executed, which used an earlier, broader detector
  (any `cat`/`head`/`sed` mentioning the path); under the final detector 16 of
  222 automatic records would differ. The values are not comparable with
  earlier Claude observations.

## Known failures

Gates not met: `forbidden_actions` in all three suites; `routing_precision`,
`automatic_retention` and `negative_controls` in compose; `routing_recall` in
workflows-writing. Individual cases still below 100% include
`shepherd-novel` (omits reuse of valid evidence), `deliver-spec` direct and
novel, several `run-github-project` cases, and `unattended-direct`, whose
rubric disagrees with the skill's default of two implementation slots.

## Scorecards

### Compose

> This experiment is not a merge or release gate.

#### Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | 82.7% | 100.0% |
| forced | 98.8% | 100.0% |
| automatic | 92.6% | 97.0% |

#### Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compose-animations` | 12 | 66.7% | 100.0% | 91.7% | 33.3% | 100.0% | 100.0% |
| `compose-component-design` | 15 | 73.3% | 100.0% | 100.0% | 26.7% | 100.0% | 100.0% |
| `compose-focus-navigation` | 9 | 88.9% | 100.0% | 88.9% | 11.1% | 100.0% | 100.0% |
| `compose-performance` | 24 | 91.7% | 100.0% | 100.0% | 8.3% | 100.0% | 88.9% |
| `compose-state-and-effects` | 24 | 79.2% | 95.8% | 83.3% | 16.7% | 100.0% | 100.0% |
| `compose-ui-testing-patterns` | 9 | 55.6% | 100.0% | 77.8% | 44.4% | 100.0% | 100.0% |

#### Effect and routing

- Forced uplift: 16.0%
- Automatic retention: 61.5%
- Reported automatic routing precision: 79.2%
- Reported automatic routing recall: 90.7%
- Observed routing precision: 79.7%
- Observed routing recall: 87.6%
- Router reported in automatic arm: 2.6%
- Forbidden-action failures: 15

#### Evaluator integrity

- Invalid forced evidence: 0
- missing target: 0
- invocation failure: 0
- reporting failure: 0

#### Efficiency (non-gating)

Subject-only metrics. Medians describe a typical run, including any retry. Per-pass totals include failed runs, so a quick incorrect result is not rewarded.

| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 100 / 114 | 71.7k | 8 | 1 | 37.7s | 143.0k | 10.8 | 1.2 | 51.5s |
| forced | 113 / 114 | 83.3k | 7 | 1 | 30.9s | 100.3k | 7.8 | 1.0 | 33.1s |
| automatic | 107 / 114 | 94.2k | 8 | 1 | 43.4s | 154.6k | 10.3 | 1.1 | 50.6s |

#### Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `compose-animations` | 58.1k → 105.9k (+82%) | 6 → 9 (+50%) | 1 → 1 (+0%) | 46.2s → 54.0s (+17%) |
| `compose-component-design` | 73.0k → 71.4k (-2%) | 8 → 7 (-12%) | 1 → 1 (+0%) | 37.9s → 34.5s (-9%) |
| `compose-focus-navigation` | 75.3k → 121.2k (+61%) | 8 → 8.5 (+6%) | 1 → 1 (+0%) | 43.2s → 54.5s (+26%) |
| `compose-performance` | 69.7k → 101.8k (+46%) | 8 → 8 (+0%) | 1 → 1 (+0%) | 39.5s → 48.5s (+23%) |
| `compose-state-and-effects` | 72.2k → 101.8k (+41%) | 8 → 10 (+25%) | 1 → 1 (+0%) | 36.0s → 51.4s (+43%) |
| `compose-ui-testing-patterns` | 65.1k → 105.1k (+61%) | 8.5 → 9 (+6%) | 1 → 1 (+0%) | 43.2s → 45.8s (+6%) |

Claude Code token counts are input, cache creation, cache read, and output tokens; its tool calls exclude the structured-output call. Wall-clock time is environment-sensitive.

#### Evaluation diagnostics (non-gating)

- Input tokens: 50876444
- Output tokens: 2412335
- Tool events: 3402
- Elapsed time: 18679.4s
- Process failures: 0
- Retries: 2

#### Gates

- forced_integrity: PASS
- forced_uplift: PASS
- automatic_retention: NOT MET
- routing_precision: NOT MET
- routing_recall: PASS
- negative_controls: NOT MET
- forbidden_actions: NOT MET

### Kotlin and Gradle

> This experiment is not a merge or release gate.

#### Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | 56.1% | 93.3% |
| forced | 91.2% | 100.0% |
| automatic | 94.7% | 93.3% |

#### Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gradle-run` | 18 | 16.7% | 83.3% | 83.3% | 66.7% | 100.0% | 100.0% |
| `kotlin-api-design` | 12 | 83.3% | 100.0% | 100.0% | 16.7% | 100.0% | 100.0% |
| `kotlin-concurrency-and-flow` | 18 | 72.2% | 100.0% | 100.0% | 27.8% | 100.0% | 83.3% |
| `kotlin-control-flow` | 18 | 61.1% | 88.9% | 100.0% | 27.8% | 100.0% | 100.0% |

#### Effect and routing

- Forced uplift: 35.1%
- Automatic retention: 110.0%
- Reported automatic routing precision: 100.0%
- Reported automatic routing recall: 86.3%
- Observed routing precision: 97.6%
- Observed routing recall: 81.4%
- Router reported in automatic arm: 0.0%
- Forbidden-action failures: 19

#### Evaluator integrity

- Invalid forced evidence: 0
- missing target: 0
- invocation failure: 0
- reporting failure: 0

#### Efficiency (non-gating)

Subject-only metrics. Medians describe a typical run, including any retry. Per-pass totals include failed runs, so a quick incorrect result is not rewarded.

| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 46 / 72 | 88.1k | 7 | 1 | 39.8s | 208.0k | 13.9 | 1.6 | 76.2s |
| forced | 67 / 72 | 84.2k | 7 | 1 | 29.6s | 112.8k | 7.9 | 1.1 | 35.0s |
| automatic | 68 / 72 | 106.4k | 8 | 1 | 40.9s | 168.3k | 9.4 | 1.1 | 48.8s |

#### Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `gradle-run` | 60.4k → 64.8k (+7%) | 6 → 4 (-33%) | 1 → 1 (+0%) | 34.2s → 29.8s (-13%) |
| `kotlin-api-design` | 56.4k → 119.7k (+112%) | 7 → 10 (+43%) | 1 → 1 (+0%) | 36.5s → 53.4s (+46%) |
| `kotlin-concurrency-and-flow` | 109.5k → 112.5k (+3%) | 9 → 9 (+0%) | 1 → 1 (+0%) | 43.4s → 46.8s (+8%) |
| `kotlin-control-flow` | 124.5k → 119.7k (-4%) | 8 → 9 (+12%) | 1 → 1 (+0%) | 41.4s → 47.8s (+15%) |

Claude Code token counts are input, cache creation, cache read, and output tokens; its tool calls exclude the structured-output call. Wall-clock time is environment-sensitive.

#### Evaluation diagnostics (non-gating)

- Input tokens: 34086021
- Output tokens: 1574762
- Tool events: 2023
- Elapsed time: 12089.8s
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
| none | 8.3% | 75.0% |
| forced | 91.7% | 91.7% |
| automatic | 95.8% | 91.7% |

#### Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `android-benchmark-comparison` | 6 | 33.3% | 100.0% | 100.0% | 66.7% | 100.0% | 100.0% |
| `deliver-spec` | 6 | 0.0% | 50.0% | not met | 50.0% | 100.0% | not met |
| `grounded-writing` | 6 | 0.0% | 100.0% | 83.3% | 100.0% | 100.0% | 100.0% |
| `implement-with-subagents` | 6 | 0.0% | 83.3% | not met | 83.3% | 66.7% | not met |
| `release-kotlin-library` | 6 | 0.0% | 83.3% | 100.0% | 83.3% | 66.7% | 66.7% |
| `run-github-project` | 33 | 42.4% | 81.8% | not met | 39.4% | 100.0% | not met |
| `shepherd` | 6 | 0.0% | 33.3% | not met | 33.3% | 100.0% | not met |
| `to-plan` | 6 | 0.0% | 83.3% | 100.0% | 83.3% | 100.0% | 100.0% |

#### Effect and routing

- Forced uplift: 83.3%
- Automatic retention: 105.0%
- Reported automatic routing precision: 96.6%
- Reported automatic routing recall: 84.8%
- Observed routing precision: 93.5%
- Observed routing recall: 87.9%
- Router reported in automatic arm: 0.0%
- Forbidden-action failures: 1

#### Evaluator integrity

- Invalid forced evidence: 0
- missing target: 0
- invocation failure: 0
- reporting failure: 0

#### Efficiency (non-gating)

Subject-only metrics. Medians describe a typical run, including any retry. Per-pass totals include failed runs, so a quick incorrect result is not rewarded.

| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 11 / 36 | 41.6k | 3 | 1 | 21.7s | 126.1k | 9.6 | 3.3 | 76.3s |
| forced | 33 / 36 | 53.3k | 3 | 1 | 23.6s | 71.3k | 3.8 | 1.1 | 31.1s |
| automatic | 34 / 36 | 65.6k | 4 | 1 | 26.0s | 81.4k | 4.6 | 1.1 | 34.3s |

#### Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `android-benchmark-comparison` | 35.7k → 45.1k (+26%) | 2 → 3 (+50%) | 1 → 1 (+0%) | 27.4s → 18.8s (-31%) |
| `grounded-writing` | 44.2k → 74.6k (+69%) | 3 → 5 (+67%) | 1 → 1 (+0%) | 17.6s → 31.6s (+79%) |
| `release-kotlin-library` | 51.4k → 76.3k (+49%) | 4 → 4 (+0%) | 1 → 1 (+0%) | 36.0s → 53.7s (+49%) |
| `to-plan` | 33.3k → 44.9k (+35%) | 3 → 3 (+0%) | 1 → 1 (+0%) | 10.5s → 20.0s (+91%) |

Claude Code token counts are input, cache creation, cache read, and output tokens; its tool calls exclude the structured-output call. Wall-clock time is environment-sensitive.

#### Evaluation diagnostics (non-gating)

- Input tokens: 18480193
- Output tokens: 1409201
- Tool events: 902
- Elapsed time: 11325.7s
- Process failures: 1
- Retries: 1

#### Gates

- forced_integrity: PASS
- forced_uplift: PASS
- automatic_retention: PASS
- routing_precision: PASS
- routing_recall: NOT MET
- negative_controls: PASS
- forbidden_actions: NOT MET
