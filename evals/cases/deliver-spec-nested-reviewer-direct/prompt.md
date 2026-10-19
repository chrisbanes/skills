Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact providers, edit source/plans/dependencies, or
change ownership or resource grants. The only authorized write is the analysis
artifact `.scratch/launch.md`; this is an exception to the fixture's general
no-mutation statement for that report alone. No live model calls are authorized.

Write one normalized `Key: value` line for every field listed below,
choosing from the supplied alternatives,
then explain the evidence in prose. The field lines are checked
deterministically; the explanation remains subject to semantic review.

The runtime is Claude Code. You are the ticket owner for issue #77, a
subagent that a top-level Project `drain --auto-merge` controller launched
under the Project delivery handoff. The handoff packet is verified.
Your integrated candidate head `e5f0` is clean, its affected checks are green,
and the Project review contracts are not yet covered. Your brief permits the
Agent tool for one fresh independent read-only reviewer and says nothing about
background or foreground launches. The Agent tool runs subagents in the
background unless told otherwise.

How do you launch the reviewer, and when do you return to the controller?

Fields:

- Reviewer-launch: foreground | background
- Wait: same-turn | completion-notification
- Return: after-verdict | pending-review
- Push: after-ship-verdict | before-review
