# GPT-6 targeted follow-up probes

These probes cover selected repairs in the integrated skill revisions through
`dba6e5a` (including `fe883e6`, `c308b15`, and `4bd7ecd`). The subject was
`gpt-6-luna/high`; the judge was `gpt-6-sol/high`. Final targeted runs used
three repetitions per eligible case and arm. Counts below are combined
objective and judge outcomes unless called out as a regrade or rejudgment.

| Probe | Outcome | Evidence |
| --- | ---: | --- |
| Compose screenshot-review novel case, forced + automatic | 6/6 (3/3 each) | `/private/tmp/gpt6-eval-100-probe/compose-escalated` |
| Compose direct + negative controls, forced + automatic | 12/12 (3/3 each case and arm) | `/private/tmp/gpt6-eval-100-probe/compose-controls-escalated` |
| Android benchmark novel, forced + automatic; `to-plan` direct, forced | 9/9 (3/3 per case and arm) | `/private/tmp/gpt6-eval-100-probe/workflows-escalated` |
| Workflow controls: benchmark direct raw; benchmark negative; `to-plan` discussion-only negative, unresolved-choice negative, novel, and ordinary negative | 4/6; 6/6; 1/3; 2/3; 3/3; 3/3 | `/private/tmp/gpt6-eval-100-probe/workflows-controls-escalated` |
| Kotlin router API target, forced + automatic | 6/6 (3/3 each) | `/private/tmp/gpt6-kotlin-router-template-final-target` |
| Kotlin exhaustiveness direct control, forced + automatic | 6/6 (3/3 each) | `/private/tmp/gpt6-kotlin-router-template-direct-control` |
| Kotlin open-fallback negative control, forced + automatic | 6/6 (3/3 each) | `/private/tmp/gpt6-kotlin-router-template-open-negative` |
| Final `to-plan` forced target: five cases | 15/15 (3/3 per case) | `/private/tmp/gpt6-plan-restraint-3rep-root-authorized` |

The workflow-control benchmark direct result is 4/6 on the raw packets: forced
was 3/3 and automatic was 1/3. A deterministic corrected-validator regrade
raises that direct result to 5/6; the original `automatic:1` judge verdict
remains failed. A separate corrected-validator rejudgment of the derived
packet passed both criteria. The raw subject and judge packets were not
changed. This one-packet rejudgment is separate evidence and is not added to
the 5/6 regrade or counted as a suite score. Regrade:
`/private/tmp/gpt6-eval-100-probe/workflows-controls-escalated/regraded/results.json`.
Rejudgment: `/private/tmp/gpt6-benchmark-auto1-corrected-validator-judgment.json`.
Its derived-packet provenance is
`/private/tmp/gpt6-benchmark-auto1-corrected-validator-provenance.json`.

## Scope and remaining work

These are focused results, not a full-corpus score or a causal old-versus-new
comparison. The 81-case frozen three-suite aggregates in the
[full result record](2026-09-24-gpt6-improvement-results.md) remain
authoritative; that suite has not been rerun at `dba6e5a`. In particular, the
full-suite workflow scorecard still records 50.0% forced and 61.1% automatic
positive outcomes, 88.9% automatic negative-control restraint, and one
forbidden-action failure.

The Compose state-hoisting failures were narrower than first reported: two
forced replies added an `@Preview` import without declared tooling and did not
report the setup gap. Both diffs stayed within the allowed Kotlin file. Revision
`6f21cd1` clarifies that previewable content does not require an `@Preview`
annotation and requires checking tooling before adding one. Lint and the
99-case corpus validation pass. A targeted live probe was attempted twice but
stopped before any model call because `codex --version` hung in evaluator
preflight, including after escalation. This revision has no model score yet.

Next, recheck that Compose repair and `grounded-writing` automatic negative
restraint and novel coverage; then work through `release-kotlin-library`,
`shepherd`, and remaining Compose/Kotlin routing misses. Rerun the frozen
three-suite corpus after those repairs. The
[improvement plan](2026-09-23-gpt6-improvement-plan.md) records the original
priorities and gates.
