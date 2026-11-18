# Issue 171, revision 1

Base `3d9da4774f441854a8ff4c513487301b057053ca`.
The [active plan](https://github.com/chrisbanes/skills/issues/171#issuecomment-6983241433)
has digest `b35d5f8900a9780d3ea4109573cd2a903ea6da82e21ff5466c579d4bae364ce0`.
The Project #22 binding has digest
`cfc5e733c34d0d677ac2c387523b88a28340981c4c2825624fb1a686d8cc18e7`.

## Behavioral verification

The managed Gradle workflow asked “Do the coroutine contract fixture tests
pass offline?” It ran `./gradlew --offline --no-scan test` in a dedicated
temporary copy of the fixture, with an isolated Gradle user home seeded from
the existing cache. Gradle 9.7.0 ran on the JVM 21 fixture with coroutines
1.10.2. The XML result reported **9 passed, 0 failed, 0 skipped**.

| Contract | Observed result |
| --- | --- |
| Channel handoff | Buffering spans a collector gap. A full buffer rejects `trySend` and suspends `send`. After receipt and cancellation before handling, the replacement receives the next event. |
| Pending work | The replacement handles the same ID before acknowledgement clears it. A stale acknowledgement leaves a newer ID pending. |
| Cancellation | Awaiting an independently cancelled deferred throws with an active caller. Ordinary failure still returns the fallback. |
| Timeout ownership | The boundary maps its own timeout. Nested timeout and caller cancellation propagate. A successful null is wrapped. |
| Synchronous read | The eager cache returns its previous value immediately after a write and catches up when the scheduler runs. The direct projection returns the new value during the same transition. |

The sandbox denied Gradle's local lock coordination socket on the initial
attempt. The scoped retry passed. After strengthening the pending-state
assertion, the managed workflow compiled and ran the updated tests again.
The tested build script and Kotlin test file match Git blobs
`d53ebfb8e96870c08eff13e4156eb4b7e1007a2a` and
`082f65f88b3f13660e09766e5789b2fec63a3a40`, respectively.

## Evaluation coverage

The affected Kotlin/Gradle matrix passed 16 deterministic checks, and
`npm run evals:validate` validated 300 cases. The direct navigation case
retains its bounded-channel validator. The novel navigation case requires
pending work. The cancellation triad and freshness pair cover repair,
transfer, and restraint. The evaluator omits the local Kotlin probes from
subject workspaces because they contain solutions to the cases.

Live model evaluation and independent review are outside this run. The
controller retains the protected baseline and owns delivery review.
