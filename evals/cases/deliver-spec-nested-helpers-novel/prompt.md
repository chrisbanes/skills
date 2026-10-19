Use only this supplied offline snapshot and applicable skills. Do not run the
workflow, launch agents, contact providers, edit source/plans/dependencies, or
change ownership or resource grants. The only authorized write is the analysis
artifact `.scratch/launch.md`; this is an exception to the fixture's general
no-mutation statement for that report alone. No live model calls are authorized.

Write one normalized `Key: value` line for every field listed below,
choosing from the supplied alternatives,
then explain the evidence in prose. The field lines are checked
deterministically; the explanation remains subject to semantic review.

The runtime is Claude Code. You lead delivery of issue #88 as a subagent that
a top-level Project controller launched; your brief grants further delegation
within two spare descendant slots. The plan has two independent tasks, T1 and
T2, touching disjoint files. Before dispatch, T1 needs one unresolved fact
about the cache key and T2 needs one about the serializer field order; each
fact suits a bounded read-only discovery helper. After both facts are known,
each task suits its own resumable implementation worker in its own isolated
checkout. You must integrate both and obtain independent review before you
return. You want the helpers, and later the workers, to run concurrently.

How do you launch the helpers and the workers, and when do you return?

Fields:

- Helpers: foreground-one-message | background | foreground-sequential
- Slice-workers: foreground-one-message | background | foreground-sequential
- Return: after-integration-and-review | pending-workers
