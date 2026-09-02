Refactor cache eviction so its caller owns completion, cancellation, and
failure. Preserve the supplied dispatcher for the blocking file operation and
edit only `src/main/kotlin/example/Subject.kt`.
