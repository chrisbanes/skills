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
3. Give the agent one bounded assignment using the handoff brief below. A fresh
   independent audit needs a self-contained brief rather than inherited
   conversation context.
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

Fill every field, by value or by pointer to an existing record; mark a
non-applicable field `n/a`.

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
acceptance needs it.

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
