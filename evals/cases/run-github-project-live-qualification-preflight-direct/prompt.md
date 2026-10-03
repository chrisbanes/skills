Review this Project preflight using only the supplied state. Ticket #86 is in
Ready to implement and its accepted plan requires an asynchronous live
qualification against a persistent store. The plan states three finite pass
conditions and permits one live attempt. The existing harness uses a fake
runtime, but no evidence shows it has been run against isolated instances of
the production store implementation. The board also has independent Ready
ticket #87, a documentation-only change with offline Markdown validation.
The approved code and deterministic tests for #86 can proceed without access
to the store or live execution; only its asynchronous qualification depends on
the unverified harness behavior. The controller has not claimed either ticket
yet.

Explain what must be established before #86's live qualification can be
dispatched, what the offline harness must assert, what belongs in the worker
handoff, and how to handle #87 while the evidence is missing.
Distinguish the controller's Project authority from the worker's implementation
ownership. Do not claim tickets, run checks, contact providers, launch agents,
or change files.
