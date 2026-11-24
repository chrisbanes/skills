# GitHub Project watcher

For parent scope, “Project query” in this scheduler means the binding's complete
parent/descendant/dependency graph read; Status means its logical claim state.
For the GitHub parent watcher use `--parent-id`, without a Project ID or Status
field. Every wake still requires the full Refresh Gate and each item's own role authority.

For GitHub, use the read-only
[Project Watcher command](github-binding.md#project-watcher-command). `next`
never starts a watcher. Its report is a hint to refresh, never
authority: it never satisfies the [Refresh Gate](drain-scheduler.md#refresh-gate), authorizes a
claim, merge, or close, replaces a complete Project query, or serves as a
resumption signal for a [parked claim](drain-scheduler.md#terminal-required-ci-parking). Waiting
grants nothing; run grants stay invocation-scoped and lapse when the run returns.

1. Run exactly one watcher whenever any claim or batch PR is in remote wait,
   or a human action, verified authority or decision pause, label-stopped item,
   Wayfinder human-frontier item, or assigned Wayfinder HITL attention item
   exists. When nothing qualifies, stop any running watcher and wait for
   agent notifications. Do not add controller polling, sleeps,
   `ScheduleWakeup`, `CronCreate`, `schedule`, `/loop`, or the single-PR host monitor.
   Retain the running watcher and its relay/session across unrelated agent
   events and authoritative reads when its project, repository, status field,
   PR/issue watch set, interval and deadline remain unchanged. Those events
   alone require no new watcher snapshot or restart.
2. When starting or replacing a watcher, write a baseline immediately before
   the complete Project query or targeted refetch that will arm it:
   use the binding's `snapshot` command and baseline arguments.
   Use the tracker repository for the watcher. If the change request belongs
   to a different repository or code host, use that host's change-request
   evidence and supported wait path. If the host cannot supply a wait signal,
   report the missing signal for the affected claim. Pass `--pr` for every
   in-flight ticket or batch PR in the watched repository in remote wait and every
   preserved PR there of a paused, parked, label-stopped, or authority-paused ticket,
   and `--issue` for every parked
   claim, paused or label-stopped ticket, human-frontier issue, Wayfinder human-frontier item, and
   assigned Wayfinder HITL attention item. For a targeted Project board refetch, add
   `--board-from <reporting watcher's baseline file>` and a `--refresh-pr` for
   each watched PR the following authoritative read will refresh. Keep the complete
   `--pr` watch set and write a new file. The snapshot queries only those PRs
   and newly watched PRs, preserving all other prior PR, item, and issue
   fingerprints for the next wait. For a complete read, take a full snapshot.
   A non-zero `snapshot` is an `error` under step 6: discard its
   output, launch no `wait`, and retake the snapshot before repeating the read
   it precedes.
3. After a read preceded by a successful `snapshot` completes, retain any
   running watcher whose inputs remain valid. Otherwise, consume undelivered
   completed reports under step 6 and cancel a superseded running command
   through the host's cancellation mechanism, never a process-name or
   command-line match. Confirm cancellation before launching a replacement;
   discard only confirmed cancellation results. Launch `wait` with the same
   project, repository and status-field arguments, `--pr` and `--issue` built from the completed
   read's watch set, the pre-read `--baseline <file>`, `--deadline <ISO-8601>`,
   and, when the binding sets one, `--interval <seconds>` from
   [Monitoring](github-binding.md#monitoring-optional); the default is 120. A PR
   or issue the read added to or dropped from the set reports `added` or
   `removed` on the first poll, at most one redundant wake; handle it like any
   other report. If a read unexpectedly changes the inputs of a retained
   watcher, establish its replacement through steps 2-3.
4. Use a native background-command completion notification when the host
   exposes one. Otherwise, launch the cheapest
   available subagent, briefed under [subagent selection](../../subagent-delegation/references/subagent-selection.md)
   to run that one `wait` command once and return its stdout verbatim, with no
   further delegation. After a command-tool yield, await that same command
   session through the host's supported wait mechanism, respecting its limits;
   do not launch another command or send unchanged-state progress messages.
   Deliver `changed`, `error`, `deadline` or an unexpected command failure as
   soon as it is available, preserving failure status. The controller consumes
   delivered reports and ticket-agent completions before waiting again and
   continues runnable work while monitoring runs.

   When idle on a reactive-wakeup host (such as Antigravity, where background
   commands and subagents notify automatically), end the turn with no tool calls
   to await the next notification instead of polling or calling a wait tool.
   Otherwise, wait with the host's agent-wait call (`wait_agent`). Use the
   longest timeout allowed by its current schema and higher-priority
   responsiveness rules; choose a shorter valid wait for a nearer controller
   deadline. A wait returns early on a notification. Handle a due controller
   deadline under step 6 even if its watcher report has not arrived. Otherwise,
   an empty timeout is not a remote event: retain the same watcher, baseline
   and clocks and wait again, without a
   GitHub query, status probe, restart or unchanged-state notification. Only
   the watcher owns periodic remote monitoring; ticket agents stay idle in
   remote wait. Removing bounded controller-wait renewals requires a host
   capability to suspend until completion; do not add another polling layer.

   The relay counts as one active agent: whenever a watcher is
   required and the active-agent limit exceeds one, reserve that capacity before
   [Scheduling](drain-scheduler.md#scheduling) step 7 fills it. At a limit of one, launch the relay only while no
   ticket agent runs; that agent's completion notification wakes the controller.
   A relay permitted to launch that cannot is an `error` under step 6.
5. Keep two clocks. The drain's no-progress deadline is the last productive
   wake plus 24 hours, or the drain start when there is none. A productive wake
   is any watcher report or agent notification that leads to a claim, merge, or
   dispatched work, and it resets that deadline. A wake whose refresh finds
   nothing eligible does not. Record the last productive wake in the existing
   controller checkpoint. Pass `--deadline` as the earliest of that deadline and
   every pending PR remote-wait deadline; the latter resets only per
   [Remote Waiting](drain-scheduler.md#remote-waiting). Once the no-progress deadline has been
   handled without a finish-gate return, omit it and pass only the earliest
   pending PR deadline (24 hours from the relaunch when none) until a productive
   wake starts a fresh one.
6. Read the one-line report; treat a non-zero exit or any other output as
   `error`. A confirmed cancellation under step 3 is neither a report nor a
   failure; an already completed report still requires handling.
   - For a Project board, if `changed` names only occupied-slot PRs still in the
     watch set, refetch only those tickets' PR, head, check, review, and authority
     records. Skip the Refresh Gate for this targeted refetch.
   - For any other `changed`, including every parent-scope change and changes to
     preserved PRs of paused or parked tickets, pass the Refresh Gate before any
     selection or claim.
   - `error`: a wake, never "no change". Pass the Refresh Gate and count one
     consecutive failure; `changed` and `deadline` reset the count. After three,
     stop watching. Once no local or controller action remains, apply the
     [finish gate](drain-scheduler.md#failure-isolation-and-finish-gate)'s monitoring-unavailable
     rule.
   - `deadline`: pass the Refresh Gate, apply [Remote Waiting](drain-scheduler.md#remote-waiting)
     or [batch](drain-scheduler.md#batched-post-merge-updates) timeout handling to each PR whose
     own deadline has passed, and take any
     newly runnable action. If the drain's no-progress deadline has passed, the
     [finish gate](drain-scheduler.md#failure-isolation-and-finish-gate) now returns
     `waiting-for-human` if only human-gated work remains. Otherwise relaunch
     the watcher under steps 2-3 with that deadline omitted per step 5.
