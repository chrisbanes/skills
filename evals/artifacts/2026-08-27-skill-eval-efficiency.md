# Skill evaluation change record — 2026-08-27

This record supports the correctness and efficiency snapshots published in
`README.md` and `evals/README.md`. It records the source runs, metric-selection
rules, and scorecards without turning either README into a run journal.

## Configuration

All recorded runs used Codex CLI 0.149.1. Subject runs used `gpt-5.6-terra`
with medium reasoning; blinded judging used `gpt-5.6-sol` with high reasoning.
Each condition ran three times. Subject telemetry includes input and output
tokens, completed tool calls, completed turns, and elapsed wall time. Judge
usage is excluded from skill-efficiency metrics.

The runs share repository revision
`8321e5705712bb3d664ecd671414c8d1649ebd45`. The catalog digest identifies the
exact enabled skill content for each run. Regraded artifacts preserve subject
output and telemetry while replacing judge results.

## Source runs

The source `results.json` files were retained in the operator's ignored
`.scratch/skill-evals` directory. Their SHA-256 digests identify the inputs used
to produce the scorecards below.

| Key | Suite and purpose | Conditions | Task mode | Catalog digest | `results.json` SHA-256 |
| --- | --- | ---: | --- | --- | --- |
| C0 | Compose complete run | 38 cases × 3 arms × 3 runs | edit | `a15ba553cae2acd327a6ff62ba2e75408abdfe18da59dc57be22726d288cea1a` | `46e24804c0735ea8bf5f5a319d7822293f2ebafb96d7b5b3460dbdb5c4bc1a55` |
| C1 | Compose targeted repair | 5 cases × 2 arms × 3 runs | review | `c690308f7fa051aab988b637d2de4b296ff6aae22991395761bfec5145a3d4e9` | `59b7cb6a808f24cff5b2d8f9cffaa42ce2911ce526f5e3fd6f28533787898bb0` |
| C2 | State-hoisting automatic regrade | 1 case × 1 arm × 3 runs | review | `272f4f01afea5b9e4a32f29f4391f6934e47ccd6dd6aadd2085dfd7e3166cd03` | `17c26233a0002b00b31b072556b6ae0030f94aae3d088057375a5bc614ea0cf1` |
| C3 | State-boundary automatic regrade | 1 case × 1 arm × 3 runs | review | `272f4f01afea5b9e4a32f29f4391f6934e47ccd6dd6aadd2085dfd7e3166cd03` | `9fcbe5d6b00fa653cb44d17d0d82952dcfa426c5c083f866581ff56146b10191` |
| K0 | Kotlin/Gradle complete run | 19 cases × 3 arms × 3 runs | edit | `eef12d003422bc6ee7c169101097da4a30c871ee5c5891a2d3967a286e1963e1` | `6ad166a627e2b0423cdf616494a49de8914f15d8ce47dd44dfc430e3a234d094` |
| K1 | Kotlin/Gradle targeted repair | 4 cases × 2 arms × 3 runs | edit | `a2994d565974e4b84b9536d74daa0553f05c5b92f604163561d6201548d835fc` | `5dadbd51b1b3d8ba3059c01fecd09a43fc9ac4360f1dc21755d95878df771a50` |
| K2 | Gradle router automatic regrade | 1 case × 1 arm × 3 runs | edit | `272f4f01afea5b9e4a32f29f4391f6934e47ccd6dd6aadd2085dfd7e3166cd03` | `4627f44919e0193fb1dab1b903520e1b4df9b2f4739307b66a62b323b2f4a4df` |
| W0 | Workflows/writing complete run | 12 cases × 3 arms × 3 runs | edit | `eef12d003422bc6ee7c169101097da4a30c871ee5c5891a2d3967a286e1963e1` | `39a6ba79fd0eab299d62796a3efc3a20cdea4008c936f1327f0e9f1f05d12225` |
| W1 | Workflows/writing repair | 12 cases × 2 arms × 3 runs | edit | `494b1c6d38e641bc085f9774bba6fc483f4f67ae48806e8a79b4d6bc6a33c8be` | `6260cc177276268e9445883cd2cfec488e9b9eadc9b7348ee24b22a8e5601ca5` |
| W2 | Workflows/writing regrade | 12 cases × 2 arms × 3 runs | edit | `272f4f01afea5b9e4a32f29f4391f6934e47ccd6dd6aadd2085dfd7e3166cd03` | `9e318139ef808ac2261d4959efd0e2c9b07d9caf679dbcb85c95b8936ee64b7d` |

The local sources use these paths:

- C0, K0, and W0:
  `.scratch/skill-evals/post-simplification-20260826/<suite>/results.json`.
- C1, K1, and W1:
  `.scratch/skill-evals/repair-targeted-20260827/<suite>/results.json`.
- C2:
  `.scratch/skill-evals/repair-recheck-20260827/compose-state-live/regraded/results.json`.
- C3:
  `.scratch/skill-evals/repair-recheck-20260827/compose-state-boundary-live/regraded/results.json`.
- K2:
  `.scratch/skill-evals/repair-recheck-20260827/gradle-router-live/regraded/results.json`.
- W2:
  `.scratch/skill-evals/repair-recheck-20260827/workflows-writing-live/regraded/results.json`.

For an original run directory that still contains `raw/`, recreate its detailed
generated report with
`python3 evals/run.py report --output-dir <run-directory>`. The tracked
scorecards in this record are the durable evidence; `.scratch` is not committed.

## Selection rules

- Historical baseline correctness values remain from their last certification:
  Compose in `ded78ab` and `8c87c8c`; Kotlin/Gradle in `b439cb3`, `45ff6d6`,
  and `f046bdb`. This change did not rerun or replace those baseline cells.
- A later targeted or regraded result replaces only the correctness metric and
  cases it covers. It does not replace an incomplete suite's per-run median.
- Compose efficiency uses the baseline and automatic arms from C0.
  Kotlin/Gradle efficiency uses those arms from K0.
- Workflows/writing efficiency uses the baseline and automatic arms from W0.
  W2 supports the final correctness scores but is excluded from efficiency
  because its case digests differ from W0.
- Targeted repair runs are excluded from efficiency medians because their case
  sets are incomplete and therefore not comparable with a complete arm.

The efficiency table is consequently the latest captured comparable evidence,
not a new three-arm run of every final repaired skill. A fresh complete run is
required before treating it as a current-content benchmark.

## Correctness scorecard

The published values and the evidence selected for each cell are:

| Skill | Baseline | Automatic | Restraint | Evidence |
| --- | ---: | ---: | ---: | --- |
| `compose-animations` | 75.0% | 100.0% | 100.0% | historical baseline; C0 + C1 automatic; C0 restraint |
| `compose-component-design` | 86.7% | 100.0% | 100.0% | historical baseline; C0 + C1 automatic; C0 restraint |
| `compose-focus-navigation` | 66.7% | 100.0% | 100.0% | historical baseline; C0 + C1 automatic; C0 restraint |
| `compose-performance` | 91.7% | 100.0% | 100.0% | historical baseline; C0 + C1 automatic; C0 restraint |
| `compose-state-and-effects` | 77.8% | 100.0% | 100.0% | historical baseline; C0 + C1 + C3 automatic; C0 restraint |
| `compose-ui-testing-patterns` | 55.6% | 100.0% | 100.0% | historical baseline; C0 + C1 automatic; C0 restraint |
| `gradle-run` | 33.3% | 100.0% | 100.0% | historical baseline; K0 + K1 + K2 automatic; K1 restraint |
| `kotlin-api-design` | 66.7% | 100.0% | 100.0% | historical baseline; K0 automatic; K1 restraint |
| `kotlin-concurrency-and-flow` | 33.3% | 100.0% | 100.0% | historical baseline; K0 + K1 automatic; K0 restraint |
| `kotlin-control-flow` | 27.8% | 100.0% | 100.0% | historical baseline; K0 + K1 + K2 automatic; K0 restraint |
| `grounded-writing` | — | 100.0% | 100.0% | W2 automatic and restraint |
| `implement-with-subagents` | — | 100.0% | 100.0% | W2 automatic and restraint |
| `run-github-project` | — | 100.0% | 100.0% | W2 automatic and restraint |
| `shepherd` | — | 100.0% | 100.0% | W2 automatic and restraint |

The targeted repair sequence was retained rather than hidden by the final
snapshot. C1 reached 100.0% automatic for five Compose rows, while
`compose-state-and-effects` remained at 66.7%; C3 brought the remaining state
boundary case to 100.0%. K1 reached 100.0% automatic for
`kotlin-concurrency-and-flow` and 100.0% restraint for `kotlin-api-design`; K2
brought the shared Gradle/control-flow routing case to 100.0%. W1 produced
automatic scores of 83.3%, 33.3%, 66.7%, and 100.0% respectively for the four
workflow/writing skills; W2 regrading produced 100.0% forced, automatic, and
restraint scores for all four.

## Efficiency scorecard

Values are subject-side per-run medians, baseline → automatic. Percentage
changes use the unrounded medians; displayed tokens are rounded to one decimal
thousand and counts are integers.

| Skill | Tokens / run | Tool calls / run | Turns / run | Time / run | Source |
| --- | ---: | ---: | ---: | ---: | --- |
| `compose-animations` | 41.7k → 81.9k (+96%) | 2 → 5 (+150%) | 1 → 1 (+0%) | 26.3s → 42.3s (+60%) | C0 |
| `compose-component-design` | 56.3k → 66.9k (+19%) | 3 → 3 (+0%) | 1 → 1 (+0%) | 32.6s → 29.1s (-11%) | C0 |
| `compose-focus-navigation` | 56.2k → 77.1k (+37%) | 3 → 6 (+100%) | 1 → 1 (+0%) | 32.4s → 44.1s (+36%) | C0 |
| `compose-performance` | 56.2k → 83.0k (+48%) | 3 → 4 (+33%) | 1 → 1 (+0%) | 32.5s → 40.1s (+24%) | C0 |
| `compose-state-and-effects` | 56.2k → 83.3k (+48%) | 3 → 5 (+67%) | 1 → 1 (+0%) | 28.5s → 41.6s (+46%) | C0 |
| `compose-ui-testing-patterns` | 56.7k → 69.0k (+22%) | 3 → 4 (+33%) | 1 → 1 (+0%) | 32.9s → 34.1s (+4%) | C0 |
| `gradle-run` | 70.7k → 83.3k (+18%) | 4 → 3 (-25%) | 1 → 1 (+0%) | 30.2s → 32.9s (+9%) | K0 |
| `kotlin-api-design` | 57.4k → 145.8k (+154%) | 3 → 7 (+133%) | 1 → 1 (+0%) | 30.0s → 53.0s (+77%) | K0 |
| `kotlin-concurrency-and-flow` | 72.7k → 119.2k (+64%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 46.0s → 64.2s (+40%) | K0 |
| `kotlin-control-flow` | 71.8k → 109.6k (+53%) | 4 → 5 (+25%) | 1 → 1 (+0%) | 39.1s → 53.7s (+37%) | K0 |
| `grounded-writing` | 41.3k → 65.4k (+59%) | 2 → 3 (+50%) | 1 → 1 (+0%) | 16.2s → 26.9s (+66%) | W0 |
| `implement-with-subagents` | 40.9k → 50.9k (+24%) | 2 → 2 (+0%) | 1 → 1 (+0%) | 23.7s → 25.9s (+9%) | W0 |
| `run-github-project` | 41.6k → 59.0k (+42%) | 2 → 3 (+50%) | 1 → 1 (+0%) | 25.0s → 24.1s (-3%) | W0 |
| `shepherd` | 51.8k → 74.3k (+43%) | 3 → 4 (+33%) | 1 → 1 (+0%) | 21.8s → 30.2s (+38%) | W0 |

No manual audit decision is claimed by this record. Correctness values come
from the deterministic validators and blinded judge results in the identified
artifacts.
