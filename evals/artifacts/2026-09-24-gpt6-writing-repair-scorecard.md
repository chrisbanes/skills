# Advisory Workflows and writing Skill Scorecard

> This experiment is not a merge or release gate.

## Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | not met | not met |
| forced | 83.3% | 100.0% |
| automatic | 66.7% | 100.0% |

## Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `grounded-writing` | 6 | not met | 83.3% | 66.7% | not met | 100.0% | 100.0% |

## Effect and routing

- Forced uplift: not met
- Automatic retention: not met
- Reported automatic routing precision: 100.0%
- Reported automatic routing recall: 100.0%
- Router reported in automatic arm: 0.0%
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
| none | 0 / 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| forced | 8 / 9 | 77.0k | 4 | 1 | 38.7s | 88.3k | 5.6 | 1.1 | 45.1s |
| automatic | 7 / 9 | 59.1k | 3 | 1 | 31.9s | 83.9k | 5.4 | 1.3 | 41.8s |

## Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `grounded-writing` | unavailable → 59.1k (n/a) | unavailable → 3 (n/a) | unavailable → 1 (n/a) | unavailable → 31.9s (n/a) |

Token counts are Codex input plus output tokens. Tool calls count completed command, file-change, MCP, web-search, and generic tool events. Wall-clock time is environment-sensitive.

## Evaluation diagnostics (non-gating)

- Input tokens: 2005840
- Output tokens: 39210
- Tool events: 146
- Elapsed time: 1099.5s
- Process failures: 0
- Retries: 0

## Gates

- forced_integrity: PASS
- forced_uplift: NOT MET
- automatic_retention: NOT MET
- routing_precision: PASS
- routing_recall: PASS
- negative_controls: NOT MET
- forbidden_actions: PASS
