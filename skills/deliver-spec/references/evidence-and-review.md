# Evidence and review

Keep completed work and valid evidence, while renewing what the current
candidate changes. Apply this procedure in standalone and Project delivery;
the selected mode retains its approval, authority and finish gates.

## Implementation and validation

1. Apply [Behavioral review and repair](behavioral-review.md) for demonstrated
   boundary failures, review coverage accounts, external-review convergence and
   browser failure diagnostics. It owns those rules; keep their evidence in the
   delivery record below.
2. Run affected checks while developing a slice. Run every required full check
   on meaningful integrated delivery candidates, including mandatory repository
   and provider validation. Repeat checks only when changes invalidate evidence,
   impact cannot be bounded, or an explicit repository/provider rule requires it.
   A controller handoff cannot escalate this into full checks per slice commit.
3. Reuse one concise delivery record with requirements/source pointers, scope,
   base and candidate identity, check results/log links, findings and blockers.
   Do not create temporary packets or acceptance receipts for each transition.
   Use Git identities for committed source; retain hashes for frozen datasets,
   external inputs and authenticated plan payloads where identity matters.
   Record each check's command, result and output pointer, tested commit or
   reproducible tree identity, fixed base, covered scope, and relevant dependency,
   fixture, configuration and runtime inputs. Identify uncommitted content when
   present: a commit SHA alone does not describe a dirty tree. Record review
   contract, reviewer, candidate, scope, verdict and finding dispositions with
   the same provenance. Keep these records and source pointers in the delivery
   issue/PR handoff so they survive resume; protect private evidence under the
   repository's normal storage/access rules.
4. After code, dependency, fixture, configuration, runtime or base changes,
   compare each evidence record's inputs and scope with the current candidate.
   Retain only demonstrably unaffected compatible evidence, recording why it
   still applies and which head it actually tested. Mark affected evidence
   invalid and renew it; unknown impact also requires renewal. Do not relabel
   an old result as a current-head run, or replace a mandatory full check with
   a collection of focused passes. Keep prior valid coverage distinct from
   outstanding checks and reviews.
5. Before push or acceptance, bind the combined evidence to the exact final
   clean head and recheck the selected mode's authority, native dependencies,
   qualification and CI requirements. Failed/unknown required checks,
   unresolved actionable findings, stale authority or insufficient coverage
   hold the operation. Evidence reuse never renews a grant or consumes fewer
   recorded repair attempts merely because the base changed.

## Testing and corrections

1. Let the implementation owner choose meaningful behavioral tests at established
   public boundaries where appropriate. Honor explicit test-first requests and
   repository testing policy; neither TDD nor separately approved seams is a
   universal prerequisite. Do not revert useful implementation to reconstruct a
   test-first history. Where useful, prove sensitivity with a bounded baseline
   check or intentional fault, restore the candidate and report the actual order.
2. If explicitly invoking the separately installed `tdd` skill, read its contract.
   Its mandatory user-confirmed seams and red-before-green order conflict with
   this workflow's default. Identify that exact conflict and follow the user's
   direction; do not silently edit the provider or claim TDD was performed.
3. Record routine implementation, fixture and mechanical plan corrections briefly
   in the same record and continue when requirements, coverage, architecture and
   authority are unchanged. Renew affected evidence without a plan-publication
   cycle. Material design changes require replanning; changed outcomes, weakened
   qualification, privacy policy, expanded permissions or exhausted budgets need
   the appropriate authority decision. Uncertain impact requires investigation,
   not automatic classification as a correction.
4. Default to one independent review of the integrated candidate and focused
   repair reviews. Reuse valid prior plan and implementation reviews. Require an
   earlier review only for a named risk that must be settled before proceeding;
   establish capability from runtime metadata, not a capability-only agent.

## Experiments

1. Plan the smallest credible harness that answers the approved research question.
   Justify replay infrastructure, generic runners and elaborate schemas against
   acceptance requirements; remove infrastructure without that purpose.
2. Allow independent harness work while corpus review runs. Freeze labels and
   their identity before experimental outputs are observed; review them early
   when needed to protect that boundary. Preserve requested deliverables, private
   data protections, execution budgets and applicable cancellation/recovery checks.

## Resume an integration amendment

1. Read the installed [to-plan](../../to-plan/SKILL.md) contract before selecting
   this route. It owns amendment classification, format, authentication and
   publication. If it does not support amendments, retain the normal
   full-replan path; report an unsupported amendment-only request as blocked.
   Do not invent an amendment format or treat a proposed provider change as an
   installed capability. Proven non-overlapping drift keeps the provider's
   existing screened-baseline path; an unchanged current contract needs no
   amendment.
2. Refresh and verify the provider's effective contract: original source,
   approved full plan, amendment lineage and trusted publication/readback
   evidence, applicable approval and any required early-review disposition. Check author and
   content identities against trusted anchors, not just self-consistent hashes.
   Require one unambiguous compatible chain and the exact retained candidate,
   old/new base, owner, worktree, branch/PR head and dirty-work inventory. Stop
   dependent work on foreign edits, forks/gaps, stale or unexplained candidate
   movement, ambiguous publication or an unsupported contract version; preserve
   artifacts and return the discrepancy to the planner/controller for
   reconciliation before any retry.
3. Verify unchanged requirements, acceptance, architecture and authority against
   the effective contract and actual overlap. Unknown overlap or unsupported
   preservation needs evidence before integration. Material changes need full
   replanning; permission, privacy policy or qualification changes
   also need the applicable stakeholder decision and authoritative source
   update. Unchanged issue text is not proof of unchanged impact. Keep native
   blockers, qualification, fresh authority and bounded grants independent of
   amendment validity. The Project controller alone revalidates claims/leases
   and schedules continuation; standalone publication retains `to-plan`'s
   approval gate.
4. Integrate only the authorised delta from the verified starting candidate.
   Retain completed increments, owner, branch/PR, dirty work and consumed repair
   usage; do not discard work or reset budgets to manufacture a convenient
   baseline. A pending resulting SHA permits this authorised integration, not
   acceptance. Afterward record the actual resulting commit/tree and base,
   bound to the immutable amendment/effective-contract identity, then renew
   invalidated checks and affected review under the evidence procedure above.
   Return preserved artifacts, invalidation reasons and exact remaining gates
   through the selected mode's handoff; do not recreate a lifecycle merely
   because a verified unchanged-scope amendment moved the base.

## Review the integrated candidate

1. Give the reviewer access to the existing concise record and resolving source
   pointers, using private storage/access controls where needed. Include:
   - Original requirements and acceptance criteria, approved effective plan and
     any amendment, their identities/digests, and repository standards.
   - Immutable base, candidate commit/tree and previous reviewed candidate;
     exact resolving diff and commit-list commands for the full candidate and
     any repair range, plus identified uncommitted changes. State what each
     comparison includes and excludes; a moving branch name is not a fixed base.
   - Validation provenance and compatibility/invalidation decisions, each
     required review contract, valid prior coverage and outstanding coverage.
   - Every prior finding with a stable ID, location, repair commit/diff or
     evidence-backed disposition, verification, and rationale for affected
     interactions. Keep new interaction findings separate from repaired ones.
2. Apply [Behavioral review and repair](behavioral-review.md) for first-review
   and repair scope, coverage accounts and convergence. Retain evidence under
   the implementation and validation procedure above.
3. Read each explicitly invoked review skill's actual contract before assigning
   it. Honor its scope, roles, capacity, prerequisites and output requirements:
   - `code-review` currently requires a resolving nonempty three-dot diff from
     a fixed point, tracker setup and separate Standards/Spec review agents.
     Give it that scope and procedure; do not disguise a repair-only or
     single-agent invocation as the required review.
   - `ponytail-review` covers complexity only; it cannot establish correctness
     or security acceptance.
   - `review-and-simplify-changes` retains its selected mode and scope,
     prescribed review roles/capacity (including its tiny-scope exception),
     read-only reviewers and main-only fixes. Do not delegate repairs to its
     reviewers or silently reduce a required pass.
   These examples do not replace the installed contracts. If required capacity,
   scope or procedure is unavailable, report the hard limitation and missing
   coverage. Do not suppress mandated work, credit an omitted contract or
   silently substitute another route. The bundled independent reviewer needs
   no external skill or tracker setup where it is the authorised route.
4. Require the [behavioral coverage account](behavioral-review.md) alongside
   each verdict. Return findings to the implementation owner for repair or an
   evidence-based disposition. The bundled independent route requires a `ship`, `fix-first`
   or `rethink` verdict with separate results for the required contracts. Keep
   explicitly invoked providers' required output intact and record the delivery
   gate decision separately. After repairs, renew affected validation
   and review, then confirm combined valid coverage of the final clean head
   before push. Passing focused checks or an old `ship` verdict cannot qualify
   changed code. Preserve the record's source/evidence pointers in the normal
   issue/PR handoff, including exact pending or blocked coverage.

## Finish gate

Finish only when required validation and combined independent review cover the
actual final clean candidate and all actionable findings are resolved under the
selected mode's gates. Otherwise retain the work and report the exact failed,
unknown or missing evidence/authority; never report earlier-head coverage as
current acceptance.
