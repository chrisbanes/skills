# GPT-6 inline repair probes

These targeted live runs used `gpt-6-luna/high` as subject and
`gpt-6-sol/high` as judge through the ChatGPT-bundled Codex CLI
`0.155.0-alpha.16`. The per-call figures passed to the harness were cost
planning assumptions, not measured billing. Raw packets and scorecards are in
the listed temporary directories.

The bundled CLI reported `Logged in using ChatGPT` for the later full-run
attempt. On that login, the dollar figures required by this harness do not
describe a direct API-key charge; the calls consume the account's Codex plan
allowance. [Official Codex pricing](https://learn.chatgpt.com/docs/pricing)
distinguishes ChatGPT-plan usage from API-key billing.

| Probe | Forced | Automatic | Raw output |
| --- | ---: | ---: | --- |
| Kotlin concurrency and API router controls | 6/6 | 6/6 | `/private/tmp/gpt6-inline-kotlin-smoke` |
| Compose recomposition direct, novel, and no-change | 9/9 | 9/9 | `/private/tmp/gpt6-inline-compose-smoke` |
| Compose recomposition novel after final wording | 3/3 | 3/3 | `/private/tmp/gpt6-inline-compose-final` |
| Release direct | 3/3 | 3/3 | `/private/tmp/gpt6-inline-release-order-final` |
| Release novel and no-change | 6/6 | 6/6 | `/private/tmp/gpt6-inline-release-controls-final` |
| Benchmark direct, fresh raw run | 3/3 | 3/3 | `/private/tmp/gpt6-inline-writing-benchmark-final2` |
| Writing direct and no-change before final review-gate edit | 6/6 | 6/6 | `/private/tmp/gpt6-inline-writing-final5` |
| Writing novel before final review-gate edit | 3/3 | 2/3 | `/private/tmp/gpt6-inline-writing-final5` |
| Writing novel automatic after final review-gate edit | Not run | 3/3 | `/private/tmp/gpt6-inline-writing-novel-final7` |
| Implement with subagents direct, novel, and no-change after integrated-head acceptance edit | 9/9 | Ineligible | `/private/tmp/gpt6-implement-integration-acceptance-recheck` |
| To-plan direct, novel, and no-change at `2276f9d` | 9/9 | Ineligible | `/private/tmp/gpt6-to-plan-final-preflight` |
| Benchmark reversal after explicit run-order wording | 3/3 | 3/3 | `/private/tmp/gpt6-benchmark-run-order-recheck` |

Each row is a combined objective-and-judge raw result. Each individual run has
one recorded skill-catalog digest, but the digests differ between runs and the
working-tree skill text changed during the repair sequence. These rows are
separate probes, not a uniform-head suite score. The `skill_sha` field names
the unchanged Git HEAD and does not identify the uncommitted working-tree
content. Keep the README result tables at their latest complete-suite values.

The benchmark recheck followed a deterministic matcher repair for equivalent
missing-evidence wording and a judge-packet instruction repair. The old raw
packets remain failed. A regrade and rejudge of saved packets gave separate
diagnostic evidence, while the fresh 6/6 run above establishes the new raw
result. The writing triad first ended at 17/18 because automatic novel
repetition 3 identified implementation mechanics but did not explicitly
recommend removing them. A later partial recheck still missed a separate
visible-difference request in one automatic review. The final automatic
novel recheck passed 3/3 after the review finish gate named that check.

A later two-arm workflow suite attempt at commit `ca50c6f` stopped after 41
completed raw records, of which 40 passed. Its one failure,
`implement-with-subagents-negative:forced:2`, held dispatch for an invalid
graph and shared-file overlap but called an integration report stale without
explicitly requiring affected validation at the current integrated head. The
original failed packet remains in `/private/tmp/gpt6-full-ca50c6f-workflows`.
The skill now requires that acceptance action even when another blocker also
holds dispatch; its direct, novel, and no-change forced recheck passed 9/9.
The stopped partial run is not a suite score.

A second two-arm workflow attempt at `2276f9d` stopped after 17 completed
records, 16 passing. `android-benchmark-comparison-novel:automatic:1`
recommended a "balanced comparison" without explicitly asking to balance or
reverse *run order*, leaving the next experiment ambiguous. Its failed packet
remains in `/private/tmp/gpt6-full-2276f9d-workflows`. The benchmark skill now
requires run order to be named in the recommendation; the reversal case passed
3/3 forced and 3/3 automatic in the focused recheck. This partial attempt is
also excluded from suite scores.

Local validation at the writing repair commit: `npm test` passed 171 tests with
one skip and 210 eval-harness tests. The later orchestration and benchmark
wording edits passed `npm run lint`, `python3 evals/run.py validate` (99 cases),
and `git diff --check`, with the focused live rechecks recorded above.

The remaining score gate is a frozen run across all three suites at the
integrated head, with forced and automatic outcomes reported separately and
every failure audited. For the two arms in the goal, three repetitions plan
228 Compose, 132 Kotlin/Gradle, and 90 workflow/writing records: 450 subject
and 450 judge calls, or $94.50 at the chosen per-call assumptions. The earlier
full three-arm plan also included a no-skill baseline and estimated 693 calls
per model, or $145.53. These are planning estimates, not quoted prices or
measured charges. A two-arm run verifies forced and automatic correctness but
does not refresh same-run baseline uplift or retention metrics. No aggregate
100% claim follows from the targeted probes.
