# Conversation mode

Use conversation mode for an inline task or a uniquely established source that
is not a selected GitHub issue. Separately establish the desired outcome, scope,
acceptance boundary, and every material user-facing decision. Resolve routine
implementation detail from repository evidence and the conversation.

A conversation source is decision-complete only when its stated contract plus
repository-supported details establish title, goal, success criteria, scope,
constraints, decisions, trade-offs, repository target, validation, and re-plan
boundaries with no material unresolved choice. Without an authorized,
decision-complete source:

1. Ask one recommended decision question at a time and discover facts rather
   than asking for them.
2. Continue until every required contract component is clear.
3. Present one compact self-contained summary and require confirmation before
   drafting.

When reviewing a blocked conversation source, report the next missing decision
and state that drafting remains blocked until the self-contained summary is
confirmed. A decision-complete current instruction or an already confirmed
summary needs no new confirmation.

Without an inline task, reuse prior conversation only when exactly one compact,
decision-complete summary is followed by explicit user confirmation. If Plan
mode is active, ask the user to switch to Default mode before writing; this
applies even to an already authorized source and does not require reconfirmation.

Use the decision-complete current instruction or the confirmed summary before
the user's confirmation, then inspect later messages for changes. Linked issues
and rejected options are context. Return to the interview for a later conflict
or contract-creating choice.

For a new draft, derive `.scratch/to-plan/<conversation-slug>.md` from the
authorized title: lowercase, replace runs outside `[a-z0-9]` with `-`, trim,
truncate to 60 characters and trim again, or use `plan`. Generate one lowercase
UUIDv4 plan ID. Reuse a prior path only when this conversation returned that
exact path and ID and its marker still matches; otherwise select `-2`, `-3`, and
so on. Stop rather than overwrite a missing or mismatched established marker.

Conversation mode never writes GitHub. Revalidate its draft, then return path,
baseline, validation evidence, plan ID, concise summary, and this handoff:

```text
Implement the approved implementation plan at <absolute scratch path>. Delete the plan file only after successful implementation; preserve it on blockers.
```
