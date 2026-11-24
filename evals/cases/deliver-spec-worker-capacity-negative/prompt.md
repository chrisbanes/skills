Assess three independent delivery environments for the same approved nontrivial
single-task behavior change. Source, plan, test seams and independent plan
review are current; the integration checkout is clean. The lead can edit code,
and the required behavior-test and final independent reviewer capabilities
exist. No implementation has started and neither request asks for parallelism.

A and B have the implementation skill installed. In environment A, a resumable implementation-capable worker exists, but all
currently permitted active descendant capacity is temporarily occupied by
other tasks. In environment B, the runtime has no implementation-capable
subagent at all, and no supported installation or capability expansion is
authorized. The lead has enough information to implement in either environment.

In C, a capable worker is available but only the issue delivery and planning
skills are installed. A second independent issue has permission to draft its
plan locally.

Return a JSON object keyed by A, B and C in the structured response’s
`summary` string. For A and B, return the field owner (lead or worker). For C,
return edit (boolean), missing_skill, install (boolean) and draft_plan
(boolean). Explain the decisions and how to preserve artifacts in `evidence`.
Use the supplied state and skill instructions only. Do not start agents,
install software, edit files or contact providers.
