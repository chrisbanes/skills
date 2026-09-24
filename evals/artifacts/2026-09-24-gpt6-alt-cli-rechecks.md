# GPT-6 alternate-CLI targeted rechecks

These are targeted live runs with `gpt-6-luna/high` as subject and
`gpt-6-sol/high` as judge. They used the ChatGPT-bundled Codex CLI
`0.155.0-alpha.16` because the installed Homebrew CLI did not finish its
`--version` preflight. The CLI change gives these records a separate fingerprint
from the frozen complete-suite run. The per-call cost figures were planning
assumptions, not measured billing.

| Case and revision | Forced | Automatic | Raw output |
| --- | ---: | ---: | --- |
| Compose state hoisting direct, `0aa790e` | 3/3 | 3/3 | `/private/tmp/gpt6-compose-state-hoisting-alt-cli-3rep` |
| Compose focus navigation novel, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-compose-focus-novel-alt-cli-3rep` |
| Compose recomposition performance novel, `2114de7` | 2/3 | Not run | `/private/tmp/gpt6-compose-remaining-forced-alt-cli-3rep` |
| Compose state authoring novel, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-compose-remaining-forced-alt-cli-3rep` |
| Compose state authoring novel, `ee3584e` | Not run | 3/3 | `/private/tmp/gpt6-compose-state-authoring-auto-alt-cli-3rep` |
| Compose animation/focus/testing overlap, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-compose-remaining-forced-alt-cli-3rep` |
| Kotlin Flow state/events novel, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-kotlin-flow-concurrency-alt-cli-3rep` |
| Kotlin concurrency router, `2114de7` | 3/3 | Not run | `/private/tmp/gpt6-kotlin-flow-concurrency-alt-cli-3rep` |
| Kotlin concurrency router, `ee3584e` | Not run | 2/3 | `/private/tmp/gpt6-kotlin-concurrency-router-auto-alt-cli-3rep` |
| Gradle incidental validation direct, `6f62dd7` | 3/3 | 3/3 | `/private/tmp/gpt6-gradle-incidental-alt-cli-3rep` |
| Kotlin API ownership direct, `6f62dd7` | Not run | 3/3 | `/private/tmp/gpt6-kotlin-api-ownership-auto-alt-cli-3rep` |
| Shepherd novel, `0aa790e` | 3/3 | Ineligible | `/private/tmp/gpt6-shepherd-novel-alt-cli-3rep` |
| Implement with subagents direct, novel, and no-change, `53ddfc9` | 9/9 | Ineligible | `/private/tmp/gpt6-implement-subagents-alt-cli-3rep` |
| Release direct, `0aa790e` | 2/3 | 2/3 | `/private/tmp/gpt6-release-direct-alt-cli-3rep` |
| Grounded writing direct, `ab748e1` | 3/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Grounded writing novel, `ab748e1` | 1/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Grounded writing no-change, `ab748e1` | 3/3 | 1/3 | `/private/tmp/gpt6-grounded-writing-alt-cli-3rep` |
| Release direct after ledger-order repair, `15415a2` | 3/3 | 2/3 | `/private/tmp/gpt6-release-direct-ledger-alt-cli-3rep` |
| Grounded writing direct after shared-contract repair, `15415a2` | Not run | 3/3 | `/private/tmp/gpt6-writing-direct-contract-alt-cli-3rep` |
| Android benchmark direct, `c65d99d` | Not run | 1/3 raw | `/private/tmp/gpt6-benchmark-direct-auto-alt-cli-3rep` |

The Compose revision fixed the observed preview-tooling scope miss in all six
targeted repetitions. The shepherd check-inventory revision passed all three
forced repetitions. Neither result establishes a complete-suite score.

The later Compose and Kotlin reviews were run at the same skill source revision
`2114de7`. Focus navigation, state authoring, the three-skill overlap, Flow
state/events, and the concurrency router all passed their forced-arm rechecks.
The recomposition review passed twice, but repetition 2 proposed an
`onSizeChanged` swap, equality guard, and layout-content change without
measurements establishing a need for those changes. The judge retained a
failure on its restraint criterion. The later state-authoring automatic run
passed all three repetitions at `ee3584e`, whose skill source matches
`2114de7`. Automatic arms for the other five cases remain untested at this
revision.

The source revisions differ only in this result record, but the evaluator
recorded different external skill-catalog digests for the later automatic
runs. Treat the forced and automatic rows as separate probes, not a single
paired scorecard.

The Kotlin concurrency router's later automatic run passed twice. Repetition
3 named the explicit `Route.Profile` branch but omitted using its subtype data
through the smart cast; the judge retained a branch-finding failure. The
subject reported `kotlin-concurrency-and-flow` and
`compose-state-and-effects`, rather than `kotlin-control-flow`, so the routing
and content evidence both need inspection before a skill edit.

The later Gradle incidental-validation run passed all forced and automatic
repetitions with the normalized execution evidence available to the judge.
The Kotlin API ownership automatic recheck passed all three repetitions after
the interface-implementer compatibility guidance. These are separate targeted
runs at skill source revision `6f62dd7`, not replacement suite scores.

The explicit-only `implement-with-subagents` skill passed its direct, novel,
and no-change triad at three forced repetitions each on revision `53ddfc9`.
This rechecks the earlier dependency-integration, conflict, and failed-
acceptance handoff misses without broadening its automatic eligibility.

The later benchmark direct automatic run has two failed raw packets. In
repetition 2, the edited `comparison.md` says neither raw results nor traces
are included, but the deterministic matcher rejects that equivalent missing-
evidence phrasing. In repetitions 2 and 3, the judge says `comparison.md` is
absent although the captured subject diff changes that file. These are
evaluator disagreements, not evidence that the subject omitted the file. Keep
both raw results failed until the matcher and judge-packet instructions are
repaired and the saved packets are separately regraded or rejudged. Do not
count a manual audit as a raw model pass.

In the pre-ledger release run, one forced and one automatic subject placed
bounded streaming only in prerelease history, omitting it from the final stable
summary. The revised release procedure drafts the stable summary from surviving
coverage-ledger rows before grouping history. Its recheck fixed that omission
in all six packets. The remaining automatic packet passed the deterministic
changelog validator but failed the judge's approval-handoff criterion: it
called the known publishing mechanism pending and referred to notes “shown
below” without presenting them there. The original judge verdict is retained.

The writing triad on `ab748e1` exposed three distinct issues. Two automatic
direct rewrites dropped the supplied shared public API guarantee; the later
shared-contract guidance passed a three-repetition automatic direct recheck.
Two forced and two automatic novel reviews still omitted some combination of
the conditional return-to-Full behavior, setting choice, or practical trade-off.
Two automatic no-change subjects made unnecessary edits to an adequate internal
report. The objective restraint failures stand even when the judge accepted the
content. The novel and no-change misses remain open; there is no post-repair
full writing triad.

All rows are combined objective-and-judge outcomes from the raw results, not
regraded or rejudged values. Each listed run has a uniform skill source SHA and
catalog digest within that run. Do not splice rows into a new suite score or
replace the README result tables from these focused probes.

Before a full rerun, repair and recheck the grounded-writing novel and no-change
cases, and resolve the release approval-handoff miss. At the current planning
assumptions, a three-suite, three-repetition run requires 693 subject and 693
judge calls and estimates $145.53; this is not a quoted price or an approved
spend. Keep the frozen full-suite results as the latest complete-suite evidence
until a new uniform-head run finishes and its failures are audited.

## Ready repair work

The remaining skill edits are independent and may be implemented serially
from this integrated head. Neither requires a change to the corpus or judge
rubric to explain the recorded miss.

1. **Writing review and restraint** (`Depends on: none`): inspect all six
   novel packets, including four failures, and the no-change controls in the
   writing triad above.
   Forced novel repetitions 1 and 2 proposed dropping the cooldown sentence
   without conditionally preserving the reader-visible return to `Full`;
   automatic novel repetitions 1 and 2 also omitted either explicit setting
   choice or the practical trade-off. Automatic no-change repetitions 1 and 3
   edited an approved internal report for optional reproducibility or wording
   polish. Keep a review-specific check for supported public behavior,
   choice, trade-off, and limitation, and make the material-edit threshold
   decisive before writing. Preserve the already passing direct-contract
   behavior. Acceptance requires direct, novel, and no-change cases in forced
   and automatic arms, three repetitions each, plus a review of every failure.
2. **Release approval handoff** (`Depends on: none`): inspect automatic
   repetition 3 in the repaired release run. The deterministic changelog check
   passed, but the judge found the final handoff called the known
   `com.vanniktech.maven.publish` mechanism pending and referred to notes
   “shown below” without presenting them. Ensure a preparation-only handoff
   names the verified publishing mechanism and shows actual notes or a directly
   reviewable diff, while leaving unknown route, artifact destination, and
   validation state explicitly pending. Preserve the publication-approval
   boundary and no-change readiness behavior. Acceptance requires release
   direct, novel, and no-change cases in each eligible arm with three
   repetitions, and inspection of any remaining objective/judge disagreement.
3. **Compose performance review restraint** (`Depends on: none`): inspect
   `compose-recomposition-performance-novel:forced:2` in the later Compose run.
   It identified the layout-to-composition feedback risk but proposed an
   unmeasured callback change, redundant equality guard, and label-layout
   change. Keep the diagnosis and require measured evidence before proposing
   a stability or layout rewrite. Preserve the direct and no-change controls;
   recheck the affected direct, novel, and no-change cases with three
   repetitions in each eligible arm.
4. **Kotlin branch routing and smart-cast review** (`Depends on: none`):
   inspect `router-kotlin-concurrency-control:automatic:3` in the later Kotlin
   run. The Flow recommendation handled single-consumer versus broadcast
   delivery, but the branch review stopped at exhaustiveness and did not use
   `Route.Profile` subtype data through the smart cast. Check automatic skill
   selection as well as the review advice. Keep the counterexample where no
   independent branch decision exists; recheck the router cases in forced and
   automatic arms with three repetitions each.
5. **Benchmark evaluator evidence** (`Depends on: none`): inspect benchmark
   direct automatic repetitions 2 and 3. Extend the deterministic missing-
   evidence matcher to accept the subject's equivalent “neither raw results nor
   traces are included” wording while retaining invented-count guards. Make
   the judge treat the supplied diff as the authoritative record of edited
   files rather than inferring absence from its read-only review workspace.
   Add narrow tests for both saved packets and counterexamples, then regrade
   and rejudge without altering the original packets. A fresh model run is
   required for a new raw score at a changed evaluator fingerprint.

After the accepted repairs are integrated, freeze the skill catalog and run
the full corpus with the selected CLI and model pair. Inspect every failure and
forbidden action before updating the two README result tables. Report forced
and automatic outcomes separately; do not infer 100% from targeted checks.
