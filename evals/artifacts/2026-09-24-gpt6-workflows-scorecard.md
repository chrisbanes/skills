# Advisory Workflows and writing Skill Scorecard

> This experiment is not a merge or release gate.

## Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | 11.1% | 66.7% |
| forced | 50.0% | 100.0% |
| automatic | 61.1% | 88.9% |

## Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `android-benchmark-comparison` | 6 | 33.3% | 16.7% | 50.0% | -16.7% | 100.0% | 100.0% |
| `grounded-writing` | 6 | 0.0% | 66.7% | 50.0% | 66.7% | 100.0% | 66.7% |
| `implement-with-subagents` | 6 | 33.3% | 66.7% | not met | 33.3% | 100.0% | not met |
| `release-kotlin-library` | 6 | 0.0% | 66.7% | 83.3% | 66.7% | 100.0% | 100.0% |
| `run-github-project` | 6 | 16.7% | 100.0% | not met | 83.3% | 100.0% | not met |
| `shepherd` | 6 | 33.3% | 66.7% | not met | 33.3% | 100.0% | not met |
| `to-plan` | 6 | 0.0% | 50.0% | not met | 50.0% | 66.7% | not met |

## Effect and routing

- Forced uplift: 38.9%
- Automatic retention: 128.6%
- Reported automatic routing precision: 92.3%
- Reported automatic routing recall: 100.0%
- Router reported in automatic arm: 0.0%
- Forbidden-action failures: 1

## Evaluator integrity

- Invalid forced evidence: 0
- missing target: 0
- invocation failure: 0
- reporting failure: 0

## Efficiency (non-gating)

Subject-only metrics. Medians describe a typical run, including any retry. Per-pass totals include failed runs, so a quick incorrect result is not rewarded.

| Arm | Passes / runs | Tokens / run | Tool calls / run | Turns / run | Time / run | Tokens / pass | Tool calls / pass | Turns / pass | Time / pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 8 / 27 | 64.5k | 3 | 1 | 26.8s | 190.6k | 11.8 | 3.4 | 101.5s |
| forced | 18 / 27 | 81.6k | 5 | 1 | 37.3s | 111.0k | 9.2 | 1.5 | 60.3s |
| automatic | 19 / 27 | 56.9k | 4 | 1 | 36.2s | 98.1k | 6.2 | 1.4 | 51.7s |

## Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `android-benchmark-comparison` | 46.9k → 53.8k (+15%) | 3 → 3 (+0%) | 1 → 1 (+0%) | 23.2s → 35.0s (+51%) |
| `grounded-writing` | 35.6k → 56.9k (+60%) | 2 → 4 (+100%) | 1 → 1 (+0%) | 23.2s → 22.1s (-5%) |
| `release-kotlin-library` | 70.2k → 88.3k (+26%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 42.1s → 43.9s (+4%) |

Token counts are Codex input plus output tokens. Tool calls count completed command, file-change, MCP, web-search, and generic tool events. Wall-clock time is environment-sensitive.

## Evaluation diagnostics (non-gating)

- Input tokens: 14767448
- Output tokens: 302181
- Tool events: 950
- Elapsed time: 8178.1s
- Process failures: 0
- Retries: 0

## Gates

- forced_integrity: PASS
- forced_uplift: PASS
- automatic_retention: PASS
- routing_precision: PASS
- routing_recall: PASS
- negative_controls: PASS
- forbidden_actions: NOT MET
