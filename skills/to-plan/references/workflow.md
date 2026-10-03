# Shared workflow

## Establish context and baseline

Read repository instructions. Resolve checkout root, branch, `HEAD`, and
normalized GitHub remotes without exposing credentials. Verify a selected issue
belongs to this checkout or GitHub-verified fork; use the current checkout and
authorized title for conversation mode. Use `.scratch/to-plan/<issue-number>.md`
in GitHub mode; conversation paths are defined by its mode contract.

Inventory tracked and untracked changes. Exclude only paths that cannot affect
planned behavior, files, symbols, seams, contracts, or validation; inspect
contents only when overlap is plausible. Stop on overlap or uncertainty and
record whether each allowed entry was excluded by path or content. Never expose,
stash, reset, clean, delete, or commit user work. The baseline is committed
`HEAD`, never an in-progress diff.

## Validate and discover

For GitHub, enforce its source-packet and readiness contract. For conversation,
require the source plus repository-supported details to establish goal, success
criteria, scope, constraints, decisions, and trade-offs. Every criterion maps
to automated or precise manual verification; stop on identity or readiness
failure.

Inspect the smallest sufficient domain docs, ADRs, code, tests, configuration,
and relevant history. Prefer established public seams and testing precedent;
choose the highest practical seam and record a rationale where choices overlap.
For non-trivial work use at most two justified, bounded read-only discovery
agents; verify their evidence and retain decisions and mutations centrally.
For an autonomous replan, preserve committed base, inspect only verified report,
retained branch/PR, and dirty-work summary; never mutate its worktree or demand
a WIP commit.

Run focused existing validation to prove proposed files, symbols, seams, and
commands exist and the baseline is green. For unavailable credentials, hardware,
or services, use repository configuration or recent trusted CI evidence and
assign the omitted check to implementation; block without either source. Record
the concrete repository facts needed to execute: affected files and
ownership/interfaces, useful entry symbols, test seams, commands and working
directories. Trace control/data flow far enough to settle material decisions.
Include call-site wiring, created symbols and error branches when they remove
real ambiguity or protect a safety boundary; never invent repository facts.

## Resolve decisions and draft

Before drafting, identify assumptions whose failure would invalidate the chosen
approach or cause substantial rework. Resolve them with proportionate
repository evidence or read-only checks when practical, and record the finding.
If only new code, target hardware, or the target runtime can test an assumption,
make a bounded proof the first prerequisite of dependent implementation. State
the hypothesis, setup, observable pass/fail condition, and what stops or triggers
replanning on failure; dependent slices must name the proof task ID. Do not add a
proof when existing evidence settles the assumption, and do not leave unresolved
design choices as open-ended implementation exploration.

Before slicing, make a brief file-responsibility map from the inspected code:
record the existing files and symbols that own the behavior, tests, and wiring,
then group edits into observable increments that can each receive a focused
review and verification. Include setup, documentation, and integration edits in
the increment whose behavior they support. Keep independent increments separate
when each has its own useful check; keep tightly coupled edits together when
splitting them would leave an unreviewable or untestable intermediate state.
Set boundaries around independently changeable behaviors, not just a shared
theme: when separate call sites have their own focused checks and no required
cross-dependency, plan separate increments even if they use the same formatting
rule or belong to the same feature. Combine them only when repository evidence
shows a concrete dependency that makes an intermediate state untestable or
unreviewable; name that dependency and the gated work explicitly. A common
concept or nearby files alone do not establish coupling.

Current Todo membership, a decision-complete current task, or a confirmed
conversation source authorizes the smallest coherent contract-realizing design.
Record non-obvious choices and evidence. Escalate only conflicting authority,
material user-visible outcome/scope/acceptance choices, security/privacy/
permission policy, or unsupported compatibility, irreversible migration, or
credible data-loss risks. Complete discovery first. In normal GitHub mode ask
one recommended question and require it in issue/specification/ADR; in
conversation reconfirm a compact summary; in `--auto` return all human-required
blockers together. Do not reject or split a ready source merely because it is
large.

Use exactly one plan template. Every observable slice names prerequisites,
affected files and ownership/interfaces, the intended increment, applicable tests
or focused validation, acceptance evidence, exact command plus working directory/setup/result,
and observable completion. Reference retrievable authoritative requirements by stable identity instead of
copying the specification. Conversation plans must embed the approved source
contract needed for a fresh session; a chat reference is not retrievable evidence. For a known one-function change,
a short edit description and exact acceptance check can be sufficient.
Require ordered recipes, detailed symbol inventories, wiring, material branches,
errors and failure evidence where uncertainty, safety or a necessary seam makes
that precision useful. For receipt, privacy or concurrency work, identify the
identities, transitions, boundaries and failure cases on which correctness
actually depends. Brevity cannot hide an unresolved decision or replace a
meaningful test. Do not add speculative discovery, proofs or a length cap.
Each new slice must also have a stable unique task ID (such as `T1`) and an
explicit `Depends on` list. Reserve the case-insensitive task ID `none` for the
`Depends on: none` root marker; dependencies may name only declared task IDs.
Validate that every target exists and the graph is acyclic before handoff.
Record shared-file, interface, and integration constraints, and identify which
ready tasks may safely run concurrently. Shared mutable files or a need for
another task's unmerged changes make tasks non-independent even when the graph
otherwise marks them ready. Treat older plans without dependency metadata as
one sequential chain in listed order; new plans must include the metadata.
Let the owner choose meaningful behavioral tests under repository policy and
explicit user requests; do not require TDD or separate seam approval by default.
Do not revert useful code to recreate test-first history; use a bounded baseline
check or intentional fault where useful and report the actual testing order.
Do not leave material architecture or authority decisions to implementation.
Scale detail to risk; avoid full implementations and boilerplate. State a
shared contract once in Guardrails. Use Approach for the route, Planning
decisions for non-obvious choices, and Implementation context for current code
facts; do not repeat those sections' shared constraints in each other or in
Review focus. Each slice needs concrete affected files, validation commands and
expected results. Specify test inputs/actions and assertions when behavioral tests
apply; otherwise use focused validation without inventing a test seam. Share setup
by explicit reference. Acceptance rows should name the outcome and point to
the slice's focused check instead of paraphrasing the full contract. Omit
generic deviation and re-plan sections when only standard handoff rules apply;
keep the concise standard diagnosis, repair, and stop limits in Guardrails so
the published plan carries them. Include additional sections only for distinct
task-specific conditions.

For experiments, choose the smallest credible harness answering the research
question. Justify replay infrastructure, generic runners and elaborate schemas
against requested acceptance. Preserve every requested deliverable and applicable
privacy, budget and cancellation safeguard. Independent harness work may proceed
while corpus review runs; freeze labels before observing experimental outputs.

Default to independent review of the integrated delivery candidate, followed by
focused repair reviews. Require earlier independent review only for a concrete
risk that must be resolved first, such as the label-freeze boundary. Reuse valid
plan reviews; executor-readiness below is the planner's own check, not a mandate
to dispatch another reviewer or spawn one merely to establish capability.

Perform an executor-readiness review from the written plan and its retrievable
source. For conversation mode, review the plan alone: include the approved goal,
acceptance criteria, scope, constraints and material decisions in the artifact,
without relying on chat history. A fresh executor must locate and order the increments, understand
ownership and interfaces, create meaningful tests and validate without reopening
material decisions. Routine implementation choices within that contract remain
with the executor; missing authority, behavior or architecture decisions do not.
Resolve gaps through discovery; put unresolvable ones in the blocker set.

Trace every source requirement to an acceptance row and implementing slice.
Check paths, interfaces, task dependencies and validation commands agree across
the plan; check exact symbols and wiring where the risk requires them. Replace
“add appropriate tests” or “run relevant checks” with concrete inputs,
assertions, commands and observable results. Remove placeholders and steps that
do not advance acceptance. Keep the proof, failure and source-authority gates
above unchanged.

## Manage, publish, and hand off

Write the selected draft. Preserve compatible user edits, refresh code facts,
and stop on conflict; never replace a whole existing draft merely on rerun. In
normal GitHub mode return path, summary, and substantive active-plan changes and
wait for publication approval; in `--auto` revalidate and continue. The GitHub
mode contract owns refresh and publishing.

After GitHub publication, return issue URL, plan permalink, baseline, validation
evidence, publication mode, revision, predecessor, presentation result, and
whether the active comment was created or reused, ending:

```text
Implement <issue URL> using the approved implementation plan at <comment permalink>.
```

For an existing amendment chain or a changed published integration decision
needing durable consumption, use [integration amendments](integration-amendments.md).
Verify installed-consumer support before publication; unknown or full-plan-only
consumers block that publication and handoff. Preserve the draft or use an
authorized full replan. Neither consumer may ignore existing amendments.
Routine compatible integration follows the continuation rule below.

A verified handoff authorizes in-scope implementation, testing and repairs,
without new per-file or per-stage approvals. Record routine implementation,
fixture and mechanical plan corrections briefly in the existing delivery record
when requirements, coverage, architecture and authority remain unchanged. Do not
replan or republish merely to correct an equivalent path, fixture or test setup.
Preserve explicit execution budgets; bounded plan-mismatch diagnosis allows one
focused diagnosis and at most two repair cycles when a factual plan assumption
is wrong. Ordinary implementation/fixture repairs do not consume that allowance.

Screen baseline drift and retained work before continuation. Proven compatible
integration preserving the contract can proceed with affected evidence renewal;
unknown overlap requires investigation. Material architecture or requirements changes
need replanning; changed authority, privacy or qualification requires the
appropriate decision. Preserve work on a blocker. Replan from a clean planning
checkout at verified base, keeping dirty implementation work separately; never
invoke `to-plan` from that implementation checkout.
