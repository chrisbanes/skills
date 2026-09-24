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
all facts an executor needs: files, symbols, responsibilities, call sites,
exemplars, commands, working directories, and created symbols. Trace enough
control/data flow to decide ownership, wiring, branches, errors, and accepted
edge cases; never invent repository facts.

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

An authorized Planning transition, decision-complete current task, or confirmed
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
existing/new files and symbols, ordered edits (interfaces, ownership, control or
data flow, branches, errors, edge cases, and wiring), exact test seam/setup/
inputs/assertions and red failure or strongest practical alternative, exact
command plus working directory/setup/result, and observable green completion.
Each new slice must also have a stable unique task ID (such as `T1`) and an
explicit `Depends on` list. Reserve the case-insensitive task ID `none` for the
`Depends on: none` root marker; dependencies may name only declared task IDs.
Validate that every target exists and the graph is acyclic before handoff.
Record shared-file, interface, and integration constraints, and identify which
ready tasks may safely run concurrently. Shared mutable files or a need for
another task's unmerged changes make tasks non-independent even when the graph
otherwise marks them ready. Treat older plans without dependency metadata as
one sequential chain in listed order; new plans must include the metadata.
Use test-first slices unless an automated red test is impractical and explain
the exception. Do not leave exploration or design decisions to implementation.
Scale detail to risk; avoid full implementations and boilerplate.

Perform an executor-readiness review from the written plan alone. A fresh,
lower-capability executor must locate and order every edit, distinguish existing
from new symbols, create meaningful tests, wire consumers, and validate without
broad rediscovery. Resolve gaps through discovery; put unresolvable ones in the
blocker set.

As part of this review, trace every source requirement to an acceptance row and
its implementing slice. Check that paths, existing and new symbol names,
interfaces, call-site wiring, task dependencies, and validation commands agree
across the plan. Replace vague instructions such as “add appropriate tests” or
“run relevant checks” with concrete inputs, assertions, commands, working
directories, and observable results. Remove placeholders and steps that do not
advance an acceptance criterion. Scale the detail to the change's risk and keep
the proof, failure, and source-authority gates above unchanged.

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

An implementation checkout may descend from planned SHA only for non-overlapping
intervening changes. Within a fixed behavior, decisions, interfaces, seams, and
validation contract, repair only a mechanical mismatch (renamed private helper,
moved equivalent file, compile, or fixture error) after one focused diagnosis
and at most two repair edit-and-validation cycles across unexpected mismatches.
Normal test-first cycles do not consume this budget. Stop at a re-plan trigger,
design/contract change, overlapping baseline change, or exhausted budget; report
failure, attempted repair/validation, and remaining decision/upstream change.
Replan from a clean planning worktree at verified base, except a verified runner
replan may retain dirty implementation work separately. Never invoke `to-plan`
from that implementation worktree.
