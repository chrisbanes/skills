# GPT-6 inline repair probes

These targeted live runs used `gpt-6-luna/high` as subject and
`gpt-6-sol/high` as judge through the ChatGPT-bundled Codex CLI
`0.155.0-alpha.16`. The per-call figures passed to the harness were cost
planning assumptions, not measured billing. Raw packets and scorecards are in
the listed temporary directories.

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

Local validation after the final writing edits: `npm test` passed 171 tests
with one skip and 210 eval-harness tests; `npm run lint`,
`python3 evals/run.py validate` (99 cases), and `git diff --check` passed.

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
