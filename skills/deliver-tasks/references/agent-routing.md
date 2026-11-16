# Agent routing

Read this reference only when the trusted Project configuration has an Agent
Setup section, or when an owner fails to start. Profiles select execution
capabilities, not model tiers; they grant no authority.

1. Validate configured profiles against the runtime. Keep the user-selected
   lead model unchanged. Use `default-owner` for planners and ticket owners,
   matching read-only capabilities for discovery or evidence helpers. For
   independent review, select a configured read-only profile whose runtime role
   supports judgment-based review (investigator or equivalent); a mechanical
   checker alone is insufficient. Investigation
   of an unresolved question requires concrete evidence; independent review
   does not require an unresolved diagnosis.
2. Keep an existing ticket owner and profile for feedback, repair, and base
   reconciliation. For a new assignment, filter profiles by required capability,
   access, runtime support, and explicit user model pins. Treat `runtime-default`
   as a match for a pin only when the runtime exposes that exact model. If none
   qualify, report the affected capability blocker and continue unrelated work.
3. Select the eligible planner or ticket default, otherwise the first eligible
   profile in configuration order. For helpers without a named default, use
   the first eligible profile. Wait for temporarily busy capacity rather than
   changing an existing owner. Do not use an external service to select agents.
4. Give the selected agent a bounded brief under
   [subagent selection](subagent-selection.md). Preserve explicit model pins;
   resolve unspecified model and reasoning settings through the user's
   selection policy for that bounded assignment before dispatch. Profile
   selection alone does not resolve those settings. Record the assignment, actual
   runtime role, configured profile, and model and reasoning when exposed in
   the existing ownership record. Finish with the agent's evidence or blocker.

## Owner Start Failure

After a configured runtime/provider fails to start a ticket owner, confirm no
owner started before retrying that same profile once. An ambiguous start needs
reconciliation before any retry. If the retry fails, stop the drain and report
the provider error and preserved claims, branches, PRs and checkpoints; quiesce
active owners safely rather than abandoning their writes. Never silently switch
providers. An explicit Agent Setup fallback or current user instruction may
permit a named alternative after failed-start reconciliation; record that
authority and selection. A reversible-decision option cannot supply fallback
authority. Distinguish start failure from temporary capacity exhaustion or an
unsupported profile found before launch, which use the selection rules above.
