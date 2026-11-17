Tracker jira, site https://fixture.atlassian.net. Code host GitHub, repository acme/widgets. Each scenario is independent. The default agent-work role is ready-for-agent. All unmentioned relevant checks and grants in a snapshot pass.

- departed-claim. KAN-4 was claimed by the runner in configured In Progress with ready-for-agent. A complete fresh read of the trusted JQL excludes it. A separate exact read confirms unchanged label, status and owner.
- departed-unclaimed. KAN-5 was unclaimed and leaves the same complete selection.
- label-removed. KAN-6 remains in the result but its ready-for-agent label has been removed during a claim.
- board-subtask. KAN-7 is a To Do sub-task without a role label, although its parent carries ready-for-agent.
- board-epic. KAN-8 is an epic root carrying ready-for-agent, but it has the configured Backlog status. All its descendants are Done.
- no-backlog. KAN-8 has that same Jira status, but no Backlog ID is configured and this type maps the exact ID to To Do. The role and verified plan remain usable.
- external-blockers. KAN-9 has an inward Blocks link to inaccessible KAN-99. Its remotelink response contains `{"relationship":"is blocked by","object":{"url":"https://other.atlassian.net/browse/OPS-1","title":"OPS-1"}}`. It also has an inward Blocks link to OPS-2 from another project on the bound site, freshly verified Done. Its outward link is unrelated.
- priority-rank. Three otherwise equal unclaimed candidates in Jira ascending Rank order are A=Low, B=High, C=High. The applicable single-select option order is High, Low.
