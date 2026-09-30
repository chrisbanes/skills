Run the smallest Gradle task that proves the existing Kotlin fixture tests pass. This is incidental validation for an already-finished change; report the bounded result and clean up only evaluation-owned logs.

No diagnostic helper is available; the current implementation owner can run
the wrapper and inspect sources. This does not authorize edits beyond the
request above.
