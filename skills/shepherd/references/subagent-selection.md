# Subagent selection and handoff

Use this reference when a workflow has permitted or required a subagent. The
calling workflow owns the delegation trigger, authority, and acceptance rules;
the selected agent owns only its bounded assignment. This reference grants no
editing, remote mutation, or further delegation authority.

1. Read the user's instructions, repository agent guidance, and the calling
   workflow's role, scope, and permission requirements. Keep the selected lead
   model unchanged. If delegation is optional, stay in the current agent for
   small or tightly coupled work without an independent task.
2. Choose by required capability before runtime role name or cost. Match the
   task to bounded discovery, predetermined checking, implementation and
   repair ownership, or independent judgment-based review. Use an exceptional
   investigator for a concrete unresolved question backed by evidence, not a
   broad topic or large task. Respect configured agent and model choices; this
   reference does not pin a model or reasoning level. Confirm the chosen
   agent's actual read/write access, tools, isolation, capacity, and ability to
   persist or resume for the required work.
3. Give the agent one bounded assignment using the handoff brief below. Prefer
   pointers to existing plans, instructions, checkout state, and evidence over
   copying their contents when each recipient can retrieve the referenced
   material. Keep task-specific scope and permission differences explicit in
   the brief. Verify that every recipient can access each reference and that it
   still describes the assigned state; replace an inaccessible or stale pointer
   with a corrected reference or the smallest necessary excerpt. A pointer does
   not supply missing scope, action authority, acceptance criteria, or source
   authority. A fresh independent audit must still receive a self-contained
   brief, including the approved source, fixed base and candidate, review
   standard, and required verdict and coverage; pointers may provide supporting
   context but cannot make those essentials depend on inherited conversation.
4. After bounding the assignment, select model and reasoning together under
   the user's subagent model-selection policy. Classify the actual delegated
   work independently of the parent ticket, caller's model, or role name:
   worker and independent reviewer describe responsibilities, not model tiers.
   Preserve explicit configured selections and apply that policy to unspecified
   settings before dispatch; do not duplicate its model table here.
5. Retain the agent handle when follow-up or repair may be needed. Inspect its
   returned work and evidence under the calling workflow's acceptance rules;
   an agent's success report is not independent acceptance. Return failed work
   to the same owner when the calling workflow requires that continuity.

Finish this handoff with the selected capability and actual runtime role, the
model and reasoning level only when exposed, the bounded brief, and the result
or blocker. If a required capability is unavailable, report it to the caller;
if delegation was optional, the caller may continue solo within its own rules.

## Handoff brief

Fill every field, by value or by an accessible pointer to an existing record;
mark a non-applicable field `n/a`. Do not create a new plan, packet, or other
document solely to avoid a short inline detail when no suitable record exists.

- Objective or question.
- Exact checkout path and state: branch and base SHA, or repository state.
- Relevant instructions and evidence.
- Allowed actions and forbidden actions.
- Acceptance criteria and expected result.
- Blocker to report if it cannot proceed.
- Further delegation: allowed or forbidden.
- Implementation only: owned files, focused validation, and escalation
  triggers. Stop and return to the lead, keeping ownership, when the plan or
  requirements are ambiguous, an unowned file needs changing, an interface
  outside the task must change, or an approved test seam does not fit.
- Review only: approved source, fixed base and exact candidate head, standards,
  and verdict format: `ship`, `fix-first`, or `rethink` with a coverage account.

## Return

- Each validation or check command: command, exit code, tested SHA, short
  output tail, and path to a log holding the complete output. A read-only agent
  may cite an existing log or mark the log path `n/a`.
- Blockers.
- Decisions returned to the lead.
- Implementation only: commit SHA, base SHA, files changed, and whether the
  worktree is clean.
- Review only: verdict, findings with evidence, and coverage account.

The complete log, not the tail, is the evidence the caller inspects when
acceptance needs it. When a governing skill or wrapper forbids reading raw
output, such as `gradle-run`, report its bounded summary and run identifier
instead of a log path; that summary is the evidence, and no one reopens the raw
log.

## Claude Code

- Resume an owner with `SendMessage` to its agent ID.
- Nesting is on by default: forbid the Agent tool in the brief unless the
  caller grants further delegation.
- With no user model-selection policy, leave `model` unset so it is inherited;
  set effort only when the user asks.
- Run workers in the background and wait for the completion notification; do
  not poll or sleep.
- Before dispatching background writers, list the commit and validation
  commands they will run and have the user approve them. A worker denied
  permission anyway reports a blocker and does not seek a workaround.
- `Explore` and `Plan` are one-shot; do not use them for owners that may need
  repair or follow-up.
