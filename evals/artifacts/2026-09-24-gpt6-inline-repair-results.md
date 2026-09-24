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
| Invalid orchestration graph after clarification wording | 3/3 | Ineligible | `/private/tmp/gpt6-implement-invalid-graph-recheck` |
| Implement with subagents direct, novel, and no-change after final acceptance and clarification wording | 9/9 | Ineligible | `/private/tmp/gpt6-implement-final-triad-after-clarification` |
| Previously weak Kotlin/Gradle cases: incidental validation, API ownership, Flow events | 9/9 | 9/9 | `/private/tmp/gpt6-focused-gaps-kotlin-1` |
| Compose focus-navigation and state-authoring novel cases | 6/6 | 6/6 | `/private/tmp/gpt6-router-animation-identity-fix` |
| Compose state-hoisting direct after preview contract clarification | 3/3 | 3/3 | `/private/tmp/gpt6-state-hoisting-preview-contract` |
| Compose screenshot-review novel | 3/3 | 3/3 | `/private/tmp/gpt6-compose-screenshot-focused` |
| Focus-aware AnimatedContent overlap after router and animation guidance repair | 3/3 | 3/3 | Forced: `/private/tmp/gpt6-compose-overlap-forced-focused`; automatic: `/private/tmp/gpt6-router-animation-identity-fix` |
| Animation direct, novel, and no-change regression screen | 3/3 | 3/3 | `/private/tmp/gpt6-animation-regression-triad` |

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

A third two-arm workflow attempt at `3899d1a` stopped after 37 completed
records, 36 passing. `implement-with-subagents-direct:forced:1` accepted
task-scoped commits and called for affected validation at the integrated head,
but did not explicitly require a textual and semantic conflict check before
accepting the joined diff. The failed packet remains in
`/private/tmp/gpt6-full-3899d1a-workflows`. The first focused triad after the
acceptance wording passed four of five completed records; its invalid-graph
repetition 2 prescribed how to repair an invalid graph without the plan owner's
clarification. That stopped probe remains in
`/private/tmp/gpt6-implement-two-stage-acceptance-recheck`. The skill now
requires both integrated-head checks and a hold for plan-owner clarification.
The invalid-graph case then passed 3/3 forced in a fresh focused run. Neither
stopped attempt contributes a suite score.
The final direct, novel, and no-change orchestration recheck passed 9/9 forced
on one skill snapshot, with no forbidden actions.

A subsequent two-arm attempt from `9f6eff0` was stopped at the user's scope
question. Its saved raw records are 8/8 workflows/writing, 6/6 Kotlin/Gradle,
and 5/5 Compose, with no forbidden-action failures. The run directories are
`/private/tmp/gpt6-full-9f6eff0-workflows`,
`/private/tmp/gpt6-full-9f6eff0-kotlin`, and
`/private/tmp/gpt6-full-9f6eff0-compose`. None is a complete suite score. No
further model calls are planned until the evaluation scope is clarified.

The older complete scorecards also identify cases whose result on the current
revision is not established by the focused rows above. Compose includes
`compose-focus-navigation-novel`, `compose-state-authoring-novel`,
`compose-state-hoisting-direct`, `compose-ui-testing-patterns-novel`, and
`router-overlap-animation-focus-testing`. Kotlin/Gradle includes
`gradle-incidental-validation-direct`, `kotlin-api-ownership-direct`, and
`kotlin-flow-state-events-novel`. Current instructions address some of the
observed mistakes, but text inspection is not a new outcome score. These are
priority checks if the next run is focused; they do not replace a complete
two-arm result needed to verify a suite-wide 100% claim.

The user selected focused checks. The first one-repetition screen passed all
six Kotlin/Gradle conditions and nine of ten Compose conditions. The Compose
miss, `router-overlap-animation-focus-testing:automatic:1`, read focus and
testing guidance but skipped Compose animations and overlooked the rendered
`Text(selectedId)` outer-state capture. The forced arm loaded all three skills
and named that defect. The router now adds animation guidance for this
independent identity decision. Its first automatic recheck passed, but the
second identified the capture without saying to render from the lambda target
or testing both branches during overlap. That attempt stopped at 2/3 and
remains in `/private/tmp/gpt6-router-animation-focus-fix`. The animation skill
now names the specific review recommendation and overlap test. Its next fresh
automatic run passed 3/3. A one-repetition direct, novel, and no-change screen
of the animation skill passed 6/6 across forced and automatic arms.

The final-source Compose focus run then stopped after 16 records, 15 passing:
`compose-state-hoisting-direct:forced:1` made the plain content state-driven and
stayed within the allowed source file, but the judge demanded a Preview tooling
gap even though no `@Preview` wrapper or import was attempted. This is a judge
false negative under the conditional rubric: previous skill misses for this case
had added a Preview import without declared tooling, whereas this saved diff
did not. The original failed packet remains in
`/private/tmp/gpt6-router-animation-identity-fix`. The case rubric now states
that sample-state content need not add a wrapper and requires a setup-gap
report when a wrapper actually needs undeclared tooling. A fresh forced and
automatic run under the corrected case fingerprint passed 3/3 each. One
fingerprint-mismatch attempt exited before new model calls; the saved and
current fingerprints were compared and found equal before the same bounded
run resumed. Saved Compose packets show two catalog digests; their recorded
path lists differ by three external Sites plugin skills that appeared during the
focused work. Each selected case has one digest across its repetitions, but
the separate focused runs cannot be combined into a single suite score. No
raw packet was overwritten.

The remaining screenshot and overlap-forced cases passed their separate
three-repetition focused runs. All final focused rows above have zero
forbidden-action failures. They come from distinct case selections and, for
Kotlin/Gradle, a skill snapshot before the Compose-only wording edits; they
are not a uniform full-suite score. The result tables in the READMEs remain at
their latest published metrics.

Final local validation after the router, animation, and preview-case changes:
`npm run lint`, `python3 evals/run.py validate` (99 cases), `git diff --check`,
and `npm test` (171 tests with one skip, plus 210 eval-harness tests) passed.
The preview contract test was updated to assert the corrected conditional
boundary; the first full test run failed on its superseded phrase before that
repair.

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

## Further focused checks

At the later source snapshot, `gradle-fingerprint-diagnosis-novel` passed 3/3
forced and 3/3 automatic with no forbidden actions in
`/private/tmp/gpt6-targeted-fingerprint-3rep-20260924`. A preceding 1/1
screen in `/private/tmp/gpt6-targeted-fingerprint-20260924` is separate
evidence; its directory could not be extended because the evaluator detected a
fingerprint change. The fresh three-repetition run uses one catalog digest.

The first fresh `shepherd-novel` probe found two distinct problems. Its case
rubric prohibited all commands while the prompt expressly permitted one
forced-skill entrypoint read, and it required a single macOS verification while
the skill required the actual CI-equivalent checks and full local suite. The
case rubric now states the permitted read and the evidence-led local verification
sequence. The first corrected subject run still omitted the full-suite step; a
later reply said only “code or diff context” instead of requesting the PR diff
explicitly. The skill's finish gate now requests the exact check/log, PR diff,
head commit, and workflow configuration, and makes passing local checks a gate
before one repair push.

One judge also declined to read its evidence packet because it applied the
subject's no-command restriction to itself. The judge prompt now clarifies that
the restriction governs the subject, while permitting a read-only packet read.
Two saved subject packets passed separate rejudgment under that clarification;
their raw failed judgments remain unchanged in
`/private/tmp/gpt6-targeted-shepherd-skillfix-20260924`.

The final-source focused `shepherd` direct, novel, and no-change triad passed
3/3 each in the forced arm, with zero forbidden actions and one catalog digest:
`/private/tmp/gpt6-targeted-shepherd-triad-20260924`. Earlier stopped or failed
probes remain separate and are not counted as passes. These targeted results do
not establish a current full-corpus percentage; the README tables retain the
last complete-suite values.

## Historical failure coverage and routing precision

The selected raw packets underlying the older complete three-suite run
contained 30 distinct failed case/arm conditions in its forced and automatic
arms, before later deterministic regrades. A case-ID and arm comparison of
those packets with the later targeted `results.json` files found
a separate three-repetition raw pass for all 30 conditions. This is coverage
of the historical failure list, not a current full-corpus score: the passing
probes differ in source, case, and skill-catalog snapshots, and conditions
that passed in the old full run were not all rechecked.

One formerly failed condition, `compose-state-authoring-direct:automatic`, had
been repaired by a deterministic regrade of the old packet but lacked a later
subject run. It passed 3/3 on the current case in
`/private/tmp/gpt6-targeted-state-authoring-direct-20260924`, with no forbidden
actions. That probe reported an extra `kotlin-api-design` skill in one reply,
giving its selected-case routing precision 75%. The source showed one Compose
state encapsulation decision rather than an independent Kotlin API decision.
The router now makes that boundary explicit.

At the revised router snapshot, `compose-state-authoring-direct` and the
`compose-side-effects-negative` restraint control passed 3/3 each in the
automatic arm, with only `compose-state-and-effects` reported, zero forbidden
actions, and 100% selected-case routing precision and recall:
`/private/tmp/gpt6-targeted-compose-api-routing-20260924`. The independent
Kotlin API plus sealed-branch router control also passed 3/3 automatic with
both expected skills reported and 100% routing precision and recall:
`/private/tmp/gpt6-targeted-kotlin-api-routing-control-20260924`. Each run had
one catalog digest internally; the two runs have the same digest, while the
earlier state-authoring probe used a different catalog digest. Do not treat the
75%-to-100% comparison as a controlled causal estimate.

## Overlap routing and component review follow-up

Two older automatic router packets had extra reported skills while passing
their behavior rubrics. The animated-header case sometimes loaded
`compose-component-design`; the one-shot-navigation case sometimes loaded
`kotlin-concurrency-and-flow`. A fresh header repetition again loaded the
component skill and gave unsolicited slot/modifier advice. Another loaded it
without any component finding. Moving a scope reminder into the router's main
procedure still produced an extra component read on its first repetition, so
that unproven router edit was reverted. The header routing-precision miss remains
unresolved; the stopped packets are in
`/private/tmp/gpt6-targeted-router-overlap-precision-20260924`,
`/private/tmp/gpt6-targeted-router-overlap-final-20260924`, and
`/private/tmp/gpt6-targeted-header-scope-20260924`.

The older event-collector reply used Flow guidance for an independent delivery
and replay question within the requested one-shot navigation review. The case
now allows `kotlin-concurrency-and-flow` as an optional specialist while still
requiring `compose-state-and-effects`. At the corrected case fingerprint, all
three automatic repetitions passed, reported both skills, and identified the
delivery contract gap, with no forbidden actions and one catalog digest:
`/private/tmp/gpt6-targeted-state-event-optional-flow-20260924`.

The initial component-router control then exposed a separate real miss: one
reply identified that a `String` limits variable card content but did not
decide whether the profile region needs a slot. The component skill's review
finish check now requires a slot-versus-semantic-primitive decision for a
requested variable region. Its focused direct, no-change, and overlapping
review cases passed 3/3 each in the automatic arm, with zero forbidden actions
and one catalog digest:
`/private/tmp/gpt6-targeted-component-slot-decision-20260924`. The original
failed control packet remains in
`/private/tmp/gpt6-targeted-router-overlap-boundaries-20260924`.

These repairs improve the selected behavior and case contract. They do not
resolve the remaining header over-routing or establish a full-corpus 100% score.
