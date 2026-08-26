# Compose side effects

## Core principle

Composable bodies render; external work belongs to the smallest effect whose lifecycle matches that work.

## Procedure

1. Choose the effect from the table and keep network/business work in the appropriate screen holder unless the UI itself owns the keyed lifecycle.
2. Key an effect by the semantic input that should restart or dispose it. Do not use `Unit` to hide a changing identity, or a broad state object when one property owns the lifecycle.
3. For a long-lived effect that needs the latest callback without restarting, read a `rememberUpdatedState` value lazily inside the effect or a later callback. If a changed value should recreate work, use it as a key instead.
4. Collect event/side-effect flows in `LaunchedEffect`; collect render state near the state holder and render it as plain state. A `snapshotFlow` needs a terminal `collect`.
5. Pair every registration in `DisposableEffect` with `onDispose`; start click/gesture coroutines through `rememberCoroutineScope` rather than an event flag.
6. Route focus navigation semantics to [Compose focus navigation](../../compose-focus-navigation/SKILL.md) and measurement phase work to [Compose performance](../../compose-performance/SKILL.md).
7. Finish when work cannot run from composition, its restart/cleanup identity is explicit, and the current lifecycle owns cancellation.

| Need | API |
|---|---|
| Publish Compose state after successful recomposition | `SideEffect` |
| Register and unregister a listener/resource | `DisposableEffect(keys...)` |
| Suspending, deferred, or keyed work | `LaunchedEffect(keys...)` |
| Suspend work caused by a user event | `rememberCoroutineScope()` |
| Turn snapshot reads into a Flow | `snapshotFlow { ... }` in `LaunchedEffect` |

```kotlin
val latestOnTimeout by rememberUpdatedState(onTimeout)
LaunchedEffect(Unit) {
    delay(1_000)
    latestOnTimeout()
}
```

Do not read `latestOnTimeout` eagerly in `remember { ... }`: that snapshots its initial value. Either key `remember` on the changing value or defer the read in a lambda. Likewise, do not use `rememberUpdatedState(userId)` to avoid restarting a collection that should follow `userId`.

```kotlin
DisposableEffect(owner, observer) {
    owner.lifecycle.addObserver(observer)
    onDispose { owner.lifecycle.removeObserver(observer) }
}
```

## Exceptions

- `SideEffect` publishes after every successful recomposition; use a keyed `LaunchedEffect` for one-shot work.
- Use lifecycle-aware state collection on Android where available; use `collectAsState()` where it is not.
- For focus-derived side work, use a keyed effect or `snapshotFlow`, never an `if` in the composable body.
