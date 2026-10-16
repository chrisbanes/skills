Use supplied state only; do not contact GitHub, run commands, invoke providers
or agents, or edit files.

A `drain` has one Project watcher command running in one relay. It watches PR
#42 in an occupied remote-wait slot while an independent ticket agent works on
#61. Its baseline, watch set, interval and deadline remain valid. An unrelated
authoritative read has completed without changing any watcher input. The host
provides no native background-command completion wake. Its agent-wait tool
returns early on notifications and accepts at most 60000 ms per wait.

The controller's last agent-wait call timed out with no messages. No controller
deadline has passed, no snapshot was invalidated and there is no controller
action to take. Later, the existing relay delivers a `changed` report naming
only PR #42's `checks` field after CI fails.

Explain what happens at the empty timeout and on the later report, who keeps
monitoring GitHub, the permitted wait duration and the host-runtime boundary.
