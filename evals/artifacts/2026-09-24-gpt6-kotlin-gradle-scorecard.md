# Advisory Kotlin and Gradle Skill Scorecard

> This experiment is not a merge or release gate.

## Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | 51.0% | 100.0% |
| forced | 90.2% | 100.0% |
| automatic | 86.3% | 100.0% |

## Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gradle-run` | 12 | 41.7% | 91.7% | 91.7% | 50.0% | 100.0% | 100.0% |
| `kotlin-api-design` | 12 | 58.3% | 83.3% | 66.7% | 25.0% | 100.0% | 100.0% |
| `kotlin-concurrency-and-flow` | 18 | 44.4% | 88.9% | 88.9% | 44.4% | 100.0% | 100.0% |
| `kotlin-control-flow` | 18 | 33.3% | 83.3% | 72.2% | 50.0% | 100.0% | 100.0% |

## Effect and routing

- Forced uplift: 39.2%
- Automatic retention: 90.0%
- Reported automatic routing precision: 97.4%
- Reported automatic routing recall: 98.7%
- Router reported in automatic arm: 28.8%
- Forbidden-action failures: 0

## Evaluator integrity

- Invalid forced evidence: 0
- missing target: 0
- invocation failure: 0
- reporting failure: 0

## Efficiency (non-gating)

Subject-only metrics. Medians describe a typical run, including any retry. Per-pass totals include failed runs, so a quick incorrect result is not rewarded.

| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 41 / 66 | 60.0k | 4 | 1 | 24.1s | 93.6k | 6.6 | 1.6 | 45.5s |
| forced | 61 / 66 | 81.1k | 6 | 1 | 32.1s | 88.8k | 6.5 | 1.1 | 38.9s |
| automatic | 59 / 66 | 76.7k | 5 | 1 | 30.7s | 93.9k | 6.1 | 1.1 | 38.4s |

## Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `gradle-run` | 59.8k → 104.3k (+75%) | 4 → 7 (+75%) | 1 → 1 (+0%) | 27.6s → 45.3s (+64%) |
| `kotlin-api-design` | 60.1k → 83.9k (+40%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 32.8s → 38.8s (+18%) |
| `kotlin-concurrency-and-flow` | 60.0k → 74.0k (+23%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 26.5s → 28.0s (+6%) |
| `kotlin-control-flow` | 60.9k → 83.9k (+38%) | 5 → 5 (+0%) | 1 → 1 (+0%) | 26.2s → 38.5s (+47%) |

Token counts are Codex input plus output tokens. Tool calls count completed command, file-change, MCP, web-search, and generic tool events. Wall-clock time is environment-sensitive.

## Evaluation diagnostics (non-gating)

- Input tokens: 22841487
- Output tokens: 383149
- Tool events: 1609
- Elapsed time: 10818.5s
- Process failures: 0
- Retries: 0

## Gates

- forced_integrity: PASS
- forced_uplift: PASS
- automatic_retention: PASS
- routing_precision: PASS
- routing_recall: PASS
- negative_controls: PASS
- forbidden_actions: PASS
