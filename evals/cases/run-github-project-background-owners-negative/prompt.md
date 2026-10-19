Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact providers, edit source/plans/dependencies, or
change ownership or resource grants. The only authorized write is the analysis
artifact `.scratch/launch.md`; this is an exception to the fixture's general
no-mutation statement for that report alone. No live model calls are authorized.

Write one normalized `Key: value` line for every field listed below,
choosing from the supplied alternatives,
then explain the evidence in prose. The field lines are checked
deterministically; the explanation remains subject to semantic review.

The runtime is Claude Code. You are the top-level Project `drain`
controller, not a subagent. Issues #91 and #92 are verified, exclusively
claimed, independent, and have spare implementation capacity, so each gets its
own ticket owner. Meanwhile ticket #90's repair reproduced the same sanitized
failure twice with no new diagnostic direction, so the repair progress gate
calls for one bounded read-only evidence helper whose result you give to #90's
owner. Other runnable work remains while these agents run.

How do you launch these agents and learn that they finished? Recent guidance
says subagents must launch agents they wait on in the foreground; decide
whether that applies here.

Fields:

- Ticket-owners: background | foreground
- Evidence-helper: background | foreground
- Wait: completion-notification | poll
