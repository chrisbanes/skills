# Issue 94 scenario coverage

Source: [issue 94](https://github.com/chrisbanes/skills/issues/94) and
[approved plan](https://github.com/chrisbanes/skills/issues/94#issuecomment-5955304420).
Baseline: `b3702515bb0579521b7e94845c664c0707669ff8`.

This is a source-level procedure walkthrough and deterministic test record.
It is not a live drain, model-evaluation scorecard or measured efficiency claim.
The controller procedures are instructions; only the ranker has an executable
seam here. No external fixtures, live turns or Project mutations were used.

## Requirement mapping and walkthrough

| Requirement | Procedure / executable seam | Case and inspected outcome |
| --- | --- | --- |
| Unattended prerequisites and qualification | `execution-controller.md` Unattended readiness; authority pauses | `run-github-project-unattended-direct`: A missing visibility authority and B exhausted grant remain authority-blocked; C retains both native edge and permission blocker; D unreadable host stays unknown; E can perform its authorized next operation but is not qualified; F offline device is an execution prerequisite blocker. Unclaimed work stays unassigned; independent E continues. |
| Active delivery before speculative planning | `todo-lane.md` Yield A Planner For Delivery; scheduler priority | `run-github-project-checkpoint-novel`: one-auxiliary repair waits only until acknowledged quiescence and publication reconciliation, then resumes the same delivery owner. The planner retains owner/draft/attempts. Twelve active minutes plus forty yielded leaves eighteen active minutes, also after compaction. Unknown publication never frees capacity or causes duplicate publication. |
| Capacity and safe partial overlap | Scheduler Slot Model, Conflict Admission Gate and named-resource locks; ranker CLI | Novel case: effective active ceiling is four from runtime six/repository four/invocation five; with planner and delivery owner active, two agents may run. Slot limit is separately four. Proven disjoint slices proceed; actual shared path and later integration boundary wait. Native blockers, inseparable seams and uncertain independence delay the whole ticket. At a clean shared boundary, authority/decision-paused older integration parks the younger ticket through the existing verified pause procedure, preserving claim/owner/artifacts while releasing capacity for unrelated work. Unknown publication retains capacity; a runnable older integration keeps the younger slot; resume requires completed older integration, lease revalidation and a free slot, not merely a merge grant. |
| Freshness without repeated full hydration | Scheduler Refresh Gate; execution hydration | Novel case: three unchanged occupied-ticket CI observations use targeted reads. Merge/invalidating selection/recovery, partial reads and finish require complete valid state; an uninvalidated complete snapshot is reused only under the existing gate. Every full refresh records its reason; writes still need fresh authority. |
| Presentation-only renewal | `project-config.md` renewal; paused/parked/Wayfinder recovery; ranker CLI | `run-github-project-recovery-negative`: proven same-ID committed rename renews only with complete comparison, immutable marker binding and owner acknowledgment. Semantic changes, uncommitted binding, incomplete reads, foreign/forked/stale records and live old-lease writers stop. Renewal alone does not resume parked CI or add grants. |
| Routine integration amendment consumption | Todo effective-contract gate, normalized-ticket boundary, delivery handoff | Recovery case: baseline provider has no amendment support, so full-replan fallback remains. An explicitly supported provider's verified effective contract retains owner, slot and artifacts without Todo/Ready reset. Foreign/forked/gapped/stale or unknown contracts block; material architecture replans and permission/qualification decisions retain stakeholder gates. |
| Durable timing and stalled cycles | Scheduler Phase Timing And Stalls; ticket handoff/report | Novel case: 10 planning, 10 implementation and 4 wait minutes overlap within 15 wall minutes. Stable interval IDs prevent compaction duplication. Repeated lifecycle without an increment requires evidence and one bounded next action, not a fresh retry budget or invented saving. |
| No-change and safety invariants | Existing cases plus recovery case | Current plan/non-overlapping drift avoids amendment or plan republication; `next` remains single-ticket. Existing Backlog, native-blocker, current-column, provider, claim and review tests/cases remain. Three new cases add coverage without changing historical scores. |

## Deterministic evidence

- Capacity test `test_accepts_more_than_three_claims_with_a_permitted_limit`
  failed before the fix with exit 2, then passed with four preserved claims.
- Renewal test `test_resumes_wayfinder_with_marker_bound_configuration_renewal`
  failed before the fix with `Wayfinder reconciliation configuration changed`,
  then resumed the claim while preserving its original digest.
- CLI regressions cover over-capacity blocked claims, zero/negative/noninteger
  limits, foreign and mismatched renewal bindings, missing/empty/malformed
  evidence, absent payload digest, repeated-renewal normalization, strict
  no-renewal mismatch and Backlog-parent exclusion. All 111 ranker tests pass.
- `npm run lint`, `npm run evals:validate` (134 cases), manifest JSON parsing,
  and `git diff --check` pass. Full deterministic suite results are recorded
  with the PR's exact reviewed revision.

## Boundaries

The three new cases reuse the existing immutable workflow fixture and text
validator, with behavioral rubrics for later authorized model runs. Corpus
validation confirms their definitions, not model adherence. Amendment format,
publication and evidence/reviewer packets remain owned by `to-plan` (#95) and
`deliver-spec` (#96); the positive consumer route requires installed provider
support. No review skill, plugin version, historical result table, Ensemble code
or CI configuration changed.

Entry-point inspection covered `next`/`drain` preflight and claims, Todo and
Wayfinder planning/recovery, active/paused/parked lease renewal, setup validation,
ranker normalization and CLI, delivery handoff, freshness/finish and reporting.
This repository has no UI screens, context menus, extensions or notifications
implementing these operations. Native dependency, qualification, current-column,
exclusive ownership, exact-head review and invocation-grant gates remain required.
