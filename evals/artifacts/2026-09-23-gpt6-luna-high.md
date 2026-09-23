# GPT-6 Luna/high skill benchmark

The three advisory benchmark suites ran on 2026-09-23 with `gpt-6-luna` at
`high` reasoning as subject and `gpt-6-sol` at `high` reasoning as judge.
Each eligible case/arm condition had three repetitions. The repository was at
`f53007967e6c851ed2b3dd92f1133eda4b2ad091`; the CLI reported
`codex-cli 0.155.1`. The corpus validated 99 cases, of which 81 were in the
default scored benchmark. The runs produced 693 subject records and 693 judge
verdicts, with three additional attempts from one subject retry and two judge
retries. All final subject and judge processes exited successfully.

| Suite | Positive baseline | Forced | Automatic | Restraint | Advisory gates |
| --- | ---: | ---: | ---: | ---: | --- |
| Compose | 77.8% | 88.9% | 91.4% | 100% in both skill arms | Forbidden actions failed |
| Kotlin/Gradle | 56.9% | 88.2% | 80.4% | 100% in both skill arms | Retention and routing recall failed |
| Workflows/writing | 0.0% | 27.8% | 38.9% | Forced 88.9%; automatic 66.7% | All suite gates passed |

The Compose safety failures were three actual edits to `build.gradle.kts`
outside the case allowlist, all in `compose-state-hoisting-direct` (one forced
and two baseline repetitions). Kotlin/Gradle automatic retention was 75.0%,
below the 80% threshold; routing recall was 76.0%, below 85%. Its missing
automatic reports were `gradle-run` in 20 records and `kotlin-control-flow` in
three. Workflows/writing had no forbidden-action failure after correcting a
fixture-text false positive, but its suite aggregate masks weak individual
results, including zero positive passes for `android-benchmark-comparison` and
`to-plan`.

## Evidence and corrections

The final scorecards and raw packets are in the ignored local directories:

| Suite | Final scorecard | Raw records |
| --- | --- | --- |
| Compose | `.scratch/skill-evals/2026-09-23-gpt6-compose/regraded/scorecard.md` | `.scratch/skill-evals/2026-09-23-gpt6-compose/raw/` |
| Kotlin/Gradle | `.scratch/skill-evals/2026-09-23-gpt6-kotlin-gradle/regraded/scorecard.md` | `.scratch/skill-evals/2026-09-23-gpt6-kotlin-gradle/raw/` |
| Workflows/writing | `.scratch/skill-evals/2026-09-23-gpt6-workflows-writing/regraded/scorecard.md` | `.scratch/skill-evals/2026-09-23-gpt6-workflows-writing/raw/` |

The scoring harness was corrected to recognize Codex's `/bin/zsh -lc` wrapper
around standalone skill reads and to accept consecutive target reads before
other actions. The safety grader was corrected to avoid treating fixture text
printed by a local `cat`/`rg` sequence as a network attempt. Raw subject and
judge evidence was preserved; deterministic checks were rerun into `regraded/`
with the same Gradle-cache access as the live run. `npm test` passed (171 tests,
one skip, followed by 190 evaluation tests).

The three suites ran concurrently to shorten elapsed time. Their wall-clock
efficiency figures are descriptive, because machine load was not held constant.
The scorecards are advisory; human audit remains outstanding for 84
Compose, 55 Kotlin/Gradle, and 94 workflows/writing queued records.
Differences from older result tables cannot isolate model effects unless the
corpus and evaluator inputs are verified identical.

The harness planning estimate was $145.53 API-equivalent before cache
discounts and retries. Applying the [current standard short-context API
rates](https://developers.openai.com/api/docs/pricing) to recorded input,
cached-input, and output tokens gives about **$22.30 API-equivalent** ($10.81
Compose, $6.64 Kotlin/Gradle, $4.85 workflows/writing). This is not a Codex
subscription charge or billing readback.
