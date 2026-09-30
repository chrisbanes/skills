Task `ENCODE` has an accepted commit integrated at `1111111`. The lead then
cherry-picked the accepted `WIRE` task, producing integrated head `2222222`.
That Git operation completed, but an endpoint check affected by `WIRE` fails at
`2222222`; the integration worktree is clean. A dependent ticket is ready on
paper, and an unrelated owner branch is awaiting integration. The controller
proposes resetting to `1111111`, then cherry-picking only a fix from `WIRE`.
Review the next orchestration actions and repair ownership. Do not edit files,
run Git mutations, start agents, or contact a provider.
