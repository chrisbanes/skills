# Compose state authoring

## Core principle

Mutable local UI state must survive recomposition and notify Compose when it changes.

## Procedure

1. For a mutable value in a composable scope, use `remember { mutableStateOf(...) }` (or `rememberSaveable` when recreation must preserve it). A bare local `var` resets on recomposition and does not invalidate UI.
2. Use `mutableStateListOf`/`mutableStateMapOf` for in-place observable collection changes. With `mutableStateOf(List)`, replace the list rather than mutating it.
3. Do not mutate snapshot state from the composable body to rebuild derived data. Use `remember(keys) { ... }` for a read-only result; events and effects own mutations.
4. Route layout measurement consumed by sibling composition to [Compose performance](../../compose-performance/SKILL.md), and effect capture/lifecycle to [Side effects](side-effects.md).
5. Finish when local state has one composable owner, survives the required lifecycle, and changes invalidate the correct UI.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) { Text("$count") }
}
```

```kotlin
// Read-only derived state; no composition-time back-writing.
val merged = remember(parent, overlay) {
    if (overlay.isEmpty()) parent else parent + overlay
}
```

## Exceptions

- A local `var` inside `remember`'s producer, a non-composable callback, or a plain helper function is ordinary Kotlin state.
- Tests using `setContent` are composable scopes and follow the same rules.
- `produceState` has its own coroutine producer; do not add an inner `LaunchedEffect` just to produce it.

## Related

Focus behavior belongs in [Compose focus navigation](../../compose-focus-navigation/SKILL.md); `rememberUpdatedState` is effect-capture state, not a replacement for ordinary local UI state.
