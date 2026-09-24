# Advisory Compose Skill Scorecard

> This experiment is not a merge or release gate.

## Outcome pass rates

| Arm | Positive cases | Negative controls |
| --- | ---: | ---: |
| none | 79.0% | 100.0% |
| forced | 91.4% | 100.0% |
| automatic | 95.1% | 100.0% |

## Per-skill diagnostics

| Skill | Positive records per arm | Baseline | Forced | Automatic | Uplift | Forced restraint | Automatic restraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compose-animations` | 12 | 75.0% | 91.7% | 100.0% | 16.7% | 100.0% | 100.0% |
| `compose-component-design` | 15 | 86.7% | 100.0% | 100.0% | 13.3% | 100.0% | 100.0% |
| `compose-focus-navigation` | 9 | 33.3% | 66.7% | 100.0% | 33.3% | 100.0% | 100.0% |
| `compose-performance` | 24 | 83.3% | 95.8% | 100.0% | 12.5% | 100.0% | 100.0% |
| `compose-state-and-effects` | 24 | 83.3% | 87.5% | 95.8% | 4.2% | 100.0% | 100.0% |
| `compose-ui-testing-patterns` | 9 | 55.6% | 88.9% | 66.7% | 33.3% | 100.0% | 100.0% |

## Effect and routing

- Forced uplift: 12.3%
- Automatic retention: 130.0%
- Reported automatic routing precision: 88.9%
- Reported automatic routing recall: 98.4%
- Router reported in automatic arm: 40.4%
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
| none | 97 / 114 | 59.1k | 4 | 1 | 25.8s | 66.3k | 5.0 | 1.2 | 32.2s |
| forced | 107 / 114 | 79.3k | 6 | 1 | 33.1s | 84.9k | 6.4 | 1.1 | 38.0s |
| automatic | 110 / 114 | 78.9k | 5 | 1 | 30.3s | 84.1k | 5.6 | 1.0 | 37.5s |

## Per-skill efficiency (baseline vs automatic)

Subject-only per-run medians, baseline → automatic. Parentheses show the automatic change from baseline. Multi-skill scenarios contribute to every targeted skill row.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run |
| --- | ---: | ---: | ---: | ---: |
| `compose-animations` | 58.6k → 85.4k (+46%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 28.2s → 34.8s (+23%) |
| `compose-component-design` | 48.7k → 73.4k (+51%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 24.4s → 29.5s (+21%) |
| `compose-focus-navigation` | 59.1k → 84.9k (+44%) | 5 → 5 (+0%) | 1 → 1 (+0%) | 28.9s → 36.6s (+27%) |
| `compose-performance` | 49.1k → 85.0k (+73%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 26.4s → 31.8s (+21%) |
| `compose-state-and-effects` | 60.1k → 89.0k (+48%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 28.2s → 37.8s (+34%) |
| `compose-ui-testing-patterns` | 60.2k → 84.2k (+40%) | 5.5 → 5 (-9%) | 1 → 1 (+0%) | 27.1s → 26.8s (-1%) |

Token counts are Codex input plus output tokens. Tool calls count completed command, file-change, MCP, web-search, and generic tool events. Wall-clock time is environment-sensitive.

## Evaluation diagnostics (non-gating)

- Input tokens: 38413444
- Output tokens: 638727
- Tool events: 2804
- Elapsed time: 18259.4s
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
