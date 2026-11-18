# Issue 163 offline handoff

The controller supplied the [issue and brief](https://github.com/chrisbanes/skills/issues/163#issuecomment-6956402695)
and [active revision 1 plan](https://github.com/chrisbanes/skills/issues/163#issuecomment-6982694062).
The issue and plan were read through the GitHub connector. The controller's
Project #22 item is `PVTI_lAHOAAN4ns4BsKlazhJzXlA` on
`PVT_kwHOAAN4ns4BsKla`. The controller retains Project, tracker, PR and
qualification authority.

- Base `3d9da4774f441854a8ff4c513487301b057053ca`
- Plan digest `8d29832c9f15eda2250d78072b52aa5ff80dd12a35af54e3f7ccec4bf80351f5`
- Configuration digest `cfc5e733c34d0d677ac2c387523b88a28340981c4c2825624fb1a686d8cc18e7`
- Preservation baseline `/tmp/skills-project22.iHGKcT/evidence-baseline.txt`

## Contract coverage

| Shared operation | GitLab path and offline evidence |
| --- | --- |
| Identity, source, readiness, normalization | Exact authenticated project and issue reads, label or milestone membership, roles and logical state in the shared GitLab reference. Direct, Project and standalone planning have their own entry gates. |
| Claim, release and stop | Verified claim label plus exclusive assignment. Claim-loss stop preserves records and releases capacity after quiescence. The direct decision fixture covers ownership and loss. |
| Dependencies and hierarchy | Inward blocking links require verified tier and visibility. Unsupported tier and failed reads both block dependent lanes with distinct receipts. Descendant completeness requires a trusted current inventory when this REST binding cannot verify it. |
| Durable markers and supersession | Paginated issue notes, exact canonical payload readback and authoritative revision edges. The novel decision fixture covers presentation, no-op and ambiguous-create reconciliation. |
| Linking, merge and closure | Independent tracker and host operations, verified canonical linkage, exact effective closing set and verified tracker terminal state. The negative fixture covers native identity, a second project with the same IID, non-default base and mixed GitHub hosting. |
| Done and recovery | Fingerprint native auto-close and other verified Done inputs, preserve on drift, and reconcile ambiguous writes and unintended closure against exact readback. Unattended GitLab tracker wake and GitHub Project-specific mutations are unavailable. |

The source uses the existing sync authority and provider-neutral routing.
GitLab's note API strips CR and trailing whitespace and executes quick actions.
The note transport therefore requires LF, rejects quick actions and frames the
exact payload with a removable footer. Supersession leaves verified predecessor
notes visible. [GitLab Notes API](https://docs.gitlab.com/api/notes/#note-body-normalization)

## Qualification and evidence applicability

The [protocol](qualification-protocol.md) and [write ledger](qualification-writes.json)
are checked offline using the existing fake GitLab client test suite.
Their checks establish the proposed allowlist, attempted-write accounting,
cleanup reserve and behavior on ambiguous responses in a simulation. The fixture
has Free capability and missing default role labels. It cannot qualify the full
journey in its recorded state. A ready MR is proposed as qualification setup
within the 15-write forward allowance. Ordinary delivery retains its draft
gate. The isolated branch protocol exercises tracker-controlled closure only.
[GitLab issue links](https://docs.gitlab.com/user/project/issues/related_issues/),
[GitLab default branch](https://docs.gitlab.com/user/project/repository/branches/default/)

The corpus cases are synthetic decision fixtures. They establish corpus,
bundling and deterministic grading behavior, including rejection of unsafe
decisions. Live provider qualification, live scoring, independent candidate
review and external delivery remain controller gates.

The entrypoint byte limit, automatic eligibility matrix and read-only
grader assertion were repaired during routine integration. The protocol uses
a checked allowlist with the existing test client because the prior live guard
is scoped to code-host operations and counts a different journey. No plan
amendment or material scope expansion was applied.

## Touched paths

- `README.md`
- `evals/artifacts/issue-163/r1/offline-handoff.md`
- `evals/artifacts/issue-163/r1/qualification-protocol.md`
- `evals/artifacts/issue-163/r1/qualification-writes.json`
- `evals/cases/gitlab-tracker-claim-direct/case.json`
- `evals/cases/gitlab-tracker-claim-direct/expectations.json`
- `evals/cases/gitlab-tracker-claim-direct/overlay/gitlab-state.json`
- `evals/cases/gitlab-tracker-claim-direct/prompt.md`
- `evals/cases/gitlab-tracker-closure-negative/case.json`
- `evals/cases/gitlab-tracker-closure-negative/expectations.json`
- `evals/cases/gitlab-tracker-closure-negative/overlay/gitlab-state.json`
- `evals/cases/gitlab-tracker-closure-negative/prompt.md`
- `evals/cases/gitlab-tracker-notes-novel/case.json`
- `evals/cases/gitlab-tracker-notes-novel/expectations.json`
- `evals/cases/gitlab-tracker-notes-novel/overlay/gitlab-state.json`
- `evals/cases/gitlab-tracker-notes-novel/prompt.md`
- `evals/harness/suites.py`
- `evals/tests/test_delivery_bindings.py`
- `evals/tests/test_workflows_writing_matrix.py`
- `references/gitlab-binding.md`
- `scripts/test_gitlab_code_host_live_check.py`
- `skills/deliver-issue/SKILL.md`
- `skills/deliver-issue/references/drain-scheduler.md`
- `skills/deliver-issue/references/execution-controller.md`
- `skills/deliver-issue/references/gitlab-binding.md`
- `skills/deliver-issue/references/issue-lifecycle.md`
- `skills/deliver-issue/references/normalized-ticket.md`
- `skills/deliver-issue/references/provider-bindings.md`
- `skills/deliver-issue/references/review-and-setup.md`
- `skills/deliver-issue/references/ticket-lifecycle.md`
- `skills/deliver-issue/references/todo-lane.md`
- `skills/run-project/SKILL.md`
- `skills/run-project/references/drain-scheduler.md`
- `skills/run-project/references/execution-controller.md`
- `skills/run-project/references/gitlab-binding.md`
- `skills/run-project/references/issue-lifecycle.md`
- `skills/run-project/references/normalized-ticket.md`
- `skills/run-project/references/provider-bindings.md`
- `skills/run-project/references/review-and-setup.md`
- `skills/run-project/references/ticket-lifecycle.md`
- `skills/run-project/references/todo-lane.md`
- `skills/to-plan/SKILL.md`
- `skills/to-plan/references/drain-scheduler.md`
- `skills/to-plan/references/execution-controller.md`
- `skills/to-plan/references/github-mode.md`
- `skills/to-plan/references/gitlab-binding.md`
- `skills/to-plan/references/issue-lifecycle.md`
- `skills/to-plan/references/normalized-ticket.md`
- `skills/to-plan/references/provider-bindings.md`
- `skills/to-plan/references/review-and-setup.md`
- `skills/to-plan/references/ticket-lifecycle.md`
- `skills/to-plan/references/todo-lane.md`
