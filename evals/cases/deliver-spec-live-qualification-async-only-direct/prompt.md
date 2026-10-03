Review this approved qualification using only the supplied state. Its live
operation starts an asynchronous ephemeral job and returns execution handle
`J-9`. The provider retains the job only while active; the accepted operation
does not persist user data in an external store and has no conversation object
or archive lifecycle. The runbook allows at most three status reads in 20
seconds. The offline harness uses a fake runtime and already covers delayed
responses, assertion failure during an active job, and recovery. The plan allows
one live attempt.

Explain which preflight, offline harness and failure-recovery checks apply, and
which checks do not. State what identity and finite bound to retain for a live
attempt. Do not add a database, persistence assertion, conversation, or archive
test. Keep this read-only; do not run checks, contact providers, or change files.
