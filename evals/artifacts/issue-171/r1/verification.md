# Issue 171, revision 1

Base `3d9da4774f441854a8ff4c513487301b057053ca`.
The [active plan](https://github.com/chrisbanes/skills/issues/171#issuecomment-6983241433)
has digest `b35d5f8900a9780d3ea4109573cd2a903ea6da82e21ff5466c579d4bae364ce0`.
The Project #22 binding has digest
`cfc5e733c34d0d677ac2c387523b88a28340981c4c2825624fb1a686d8cc18e7`.

## Original behavioral verification

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
transfer, and restraint.

## Fixture isolation repair

Independent review of `d1d5ecc004e0e2e8676051f842518b7fbb0692fd` passed
all three Kotlin contracts and found that the shared fixture exposed the
probe dependency to unrelated cases and changed their case digests. The
probe source and dependency now live in a local overlay. The shared fixture
and runner match the exact base, including the evaluator's offline preflight
inputs.

From the repository root, assemble a fresh scratch fixture:

```sh
probe_scratch=$(mktemp -d)
probe_overlay=evals/artifacts/issue-171/r1/probe-overlay
cp -R evals/fixtures/kotlin-jvm "$probe_scratch/fixture"
cp -R "$probe_overlay/src/." "$probe_scratch/fixture/src"
cat "$probe_overlay/dependencies.gradle.kts" >> "$probe_scratch/fixture/build.gradle.kts"
```

From the assembled fixture, use the managed Gradle workflow with a cached
Gradle user home to run `./gradlew --offline --no-scan test`. The assembled
build script and probe source have Git blob identities
`39c38bea8e9022c2dfd434589b1ff1ea28726ab6` and
`082f65f88b3f13660e09766e5789b2fec63a3a40`, respectively.
The managed run asked “Do the isolated coroutine contract probes pass
offline?” The sandbox denied Gradle's local lock socket before tests started.
The scoped retry compiled and ran the assembled fixture, and the XML reported
**9 passed, 0 failed, 0 skipped**.

Prepared `kotlin-detached-thread-ownership-direct` without skills using the
actual evaluator at the exact base and with the repair. The staged workspaces
had identical bytes and file modes, including the existing `SubjectTest.kt`
overlay. Both yielded Git tree `7211780d3f434538d00589961e45d07ee7ccf02d`
and evaluator case digest
`2de4204098f68a4458da004a45a8e3a7f76db29e4fa8656e507491fe2e833ce6`.
The focused Kotlin/Gradle matrix and CLI checks passed all 35 tests.

The controller retains the protected baseline and owns delivery review.
This repair used offline checks and did not run live model evaluations.
