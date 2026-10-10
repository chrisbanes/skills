Use supplied state only; do not contact GitHub, run commands, invoke providers
or agents, or edit files.

A `drain` is in progress after a complete refresh. Ticket #61 is held by a
background implementation agent whose completion notification is due. Every
other ticket is Done, dependency-blocked on #61, or in Backlog. No PR is in
remote wait, no human action or authority pause exists, and no slot is idle with
runnable work.

What should the controller do while it waits for #61's agent?
