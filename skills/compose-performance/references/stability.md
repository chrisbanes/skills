# Compose stability diagnostics

## Core principle

Use compiler evidence and comparison semantics before changing a model or adding a stability promise.

## Procedure

1. Reproduce the transition, record recomposition counts or compiler reports, and confirm the Kotlin/Compose compiler mode.
2. With Kotlin 2.0.20+ strong skipping is normally enabled: restartable composables can skip with unstable parameters, but stable values compare with `equals` and unstable values compare by identity. Check churny instances and call-site lambdas before changing a type. For older or opted-out builds, account for the legacy non-skippable behavior.
3. Generate reports for the shipped variant and inspect `classes.txt`, `composables.txt`, `composables.csv`, and module metrics.
4. Identify the proven cause: false stability promise, mutable collection interface, external immutable type, or caller-created instance/lambda churn.
5. Apply the smallest truthful fix, then re-read the same report or re-measure the transition.
6. Finish only when the model's mutability and equality contract remains correct as well as more skippable.

```kotlin
if (providers.gradleProperty("composeReports").orNull == "true") {
    composeCompiler {
        reportsDestination = layout.buildDirectory.dir("compose_compiler")
        metricsDestination = layout.buildDirectory.dir("compose_compiler")
    }
}
```

| Evidence | Repair |
|---|---|
| UI state exposes `List`/`Set` that must be immutable | Use `ImmutableList`/`ImmutableSet`, converting once at the boundary |
| `@Immutable`/`@Stable` describes mutable non-snapshot state | First make it immutable or snapshot-observable; only then retain/add an annotation if truthful |
| Third-party type is genuinely immutable | Add only that type to `stabilityConfigurationFiles` |
| Lazy item gets a new lambda or derived object each parent recomposition | Hoist/remember it for the item's stable inputs |

Never annotate to silence a report: a false promise can show stale UI. If visible evidence cannot distinguish immutable data from observable mutable state, state both valid directions rather than inventing product requirements.

```kotlin
items(list, key = { it.id }) { item ->
    val onClick = remember(item.id) { { onItemClick(item.id) } }
    RowCard(onClick = onClick)
}
```

Do not expect call-site stabilization to solve deferred reads or cross-row measurement; route those to [Deferred reads](deferred-reads.md).

## Exceptions

- Do not tune a count caused by real displayed-data changes or a correctness defect.
- Keep test-only code simple when report cleanliness does not serve the test.
- Do not add third-party types to a stability configuration unless you will uphold their immutability contract.

## Related

[Diagnosis](diagnosis.md) identifies the performance axis when it is unknown.
