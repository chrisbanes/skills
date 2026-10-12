# Fast path

Use this for a small, well-understood change whose source already settles the
contract. It skips `to-plan`, not validation, independent review or authority.

## Qualify

Qualify only when every condition holds; otherwise use the full path. When in
doubt, use the full path.

1. The source is a verified `ready-for-agent` GitHub issue, or an approved local
   source, whose acceptance criteria are concrete and testable as written, and
   every blocker is complete with its required outcome in the baseline.
2. The fix location is known from the source or bounded inspection. The root
   cause is not unknown, flaky, intermittent or still under investigation.
3. No design decision, stakeholder choice or design artifact (such as a `.pen`
   file) is open or touched.
4. It changes no public or shared contract, ADR, persistence or migration,
   security, privacy or permission boundary.
5. It needs no device, benchmark, live-qualification or other gate that the
   repository's checks cannot run.
6. No `to-plan` plan or plan chain exists for the source other than its own
   runner-authored `Fast path` revision; reuse any other.
7. The expected change touches about three files or fewer. Size is a sanity
   check only; a small diff that fails conditions 1–6 does not qualify.

Record the classification once in the delivery record: each condition's
evidence, the contract digest (a digest of the source's normalized
contract-bearing text: goal, scope, constraints and acceptance criteria), and
a brief plan naming files, approach and checks. Before push and acceptance,
recompute it; a change is a failed condition.

## Deliver

1. Treat the source as the approved contract. Do not invoke `to-plan` or wait
   for plan publication approval. Standalone, the explicit request and the
   `ready-for-agent` label approve it; a local source still needs explicit
   stakeholder approval.
2. Implement solo under the [implementation procedure](implementation-mode.md),
   with affected checks, self-review and the single independent final review
   against the source's acceptance criteria and repository standards.
3. Put the brief plan and classification in the PR description.

## Escalate

Stop writes as soon as any condition fails during implementation, review or PR
feedback. Do not finish by flagging the growth in the PR. Preserve the branch,
commits, PR and evidence, and record which condition failed and why.

- Standalone: record the escalation (failed condition, branch and head) in the
  delivery record and, when a PR exists, in its description. Then invoke
  `to-plan` with the retained work as evidence and honor its gates before
  continuing.
- Project: return a replan packet to the controller under its
  [replan packet contract](../../run-github-project/references/todo-lane.md#replan-packet-contract),
  citing the fast-path plan revision as the active plan.
