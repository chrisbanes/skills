# Compose state deferred reads

## Core principle

State invalidates the phase that reads it. Read frame-rate state in layout or draw; never write observable state in a phase that invalidates the current or an earlier phase.

## Procedure

1. Confirm that scroll, animation, drag, or measured-size state is changing frequently and identify where it is read.
2. Keep a `State<T>` or provider lambda across composition, then read it in a block-form layout or draw modifier. Keep the read in composition only when it decides which composables exist.
3. Do not rebuild snapshot lists or maps from the composable body. Derive immutable values with `remember(keys) { ... }`; mutate snapshot state from events or effects instead.
4. When one item measures and another consumes the result, capture the measurement in layout and apply it during measure. Do not read that measurement in a sibling composable body.
5. Re-measure the same transition. Finish when the required phase alone invalidates and derived state cannot become stale.

```kotlin
// The State stays intact; its value is read during layout.
val offsetX = animateDpAsState(120.dp * selectedIndex)
Box(Modifier.offset { IntOffset(offsetX.value.roundToPx(), 0) })
```

| Composition-time shape | Deferred shape |
|---|---|
| `Modifier.offset(x = animatedX)` | `Modifier.offset { IntOffset(animatedX.value.roundToPx(), 0) }` |
| `Modifier.graphicsLayer(translationY = y)` | `Modifier.graphicsLayer { translationY = yProvider() }` |
| `Child(scrollOffset = listState.firstVisibleItemScrollOffset)` | `Child(scrollOffsetProvider = { listState.firstVisibleItemScrollOffset })` |

Suffix a cross-boundary lambda with `Provider` when that makes its deferred-read contract clear. `drawBehind`, `drawWithContent`, `layout`, `offset {}`, and `graphicsLayer {}` are suitable consumers.

```kotlin
// Do not back-write during composition.
val merged = remember(parent, overlay) {
    if (overlay.isEmpty()) parent else parent + overlay
}
```

For cross-row measurement, use a measure-phase helper such as [`decorateMeasureConstraints`](../../compose-component-design/references/modifier-layout.md), keep a fixed fallback while size is unknown, and compare before writing the captured size. This avoids a layout-to-composition cascade in sibling lazy items.

## Exceptions

- Keep a read in composition when it selects a UI branch.
- Do not obscure a one-shot, cheap value or a test assertion solely to defer it.
- If evidence shows recomposition is not the bottleneck, leave the simpler form.

## Related

- [Stability](stability.md) for parameter comparisons and compiler reports.
- [Compose state and effects](../../compose-state-and-effects/SKILL.md) for event/effect ownership.
