Use supplied state only; do not contact GitHub, run commands, invoke providers
or agents, or edit files.

In each independent `drain` invocation, the controller has completed a full
Project refresh. No PR is in remote wait, no work is runnable, and no agent
is working. The drain started 20 minutes ago and has had no productive wake.
The binding sets no polling interval. Only one item remains:

- #42 has a verified authority pause for missing merge permission.
- #43 is label-stopped after a maintainer removed its agent-work label.

For each scenario, explain what the controller does next, what it launches,
with which inputs, and when it may return `waiting-for-human`.
