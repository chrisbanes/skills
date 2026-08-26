# Compose modifier and layout style

## Core principle

The parent owns placement; a reusable composable owns its invariant structure.

## Procedure

1. For a composable that emits layout, declare `modifier: Modifier = Modifier` after required parameters and apply it to the root layout.
2. Put the caller modifier first in the root chain, then append intrinsic identity modifiers. Push positioning, padding, and general size decisions to the caller.
3. Build a modifier as one fluent expression. Keep one or two calls inline; format three or more calls one per line. Use `.then(if (condition) Modifier.x() else Modifier)` for a conditional segment.
4. Hoist a condition outside a layout only when the layout has no other content or visible container role. Keep it inside when the container has semantics, layout arguments, siblings, or both `if` branches contribute content.
5. Use `decorateMeasureConstraints` only when a measurement must be consumed during measure; route phase ownership and the cross-row recipe to [Deferred reads](../../compose-performance/references/deferred-reads.md).
6. Finish when callers can place the component, intrinsic structure remains local, and no refactor changes a container's visible or layout role.

```kotlin
@Composable
fun Avatar(url: String, modifier: Modifier = Modifier) {
    Image(
        painter = rememberAsyncImagePainter(url),
        contentDescription = null,
        modifier = modifier
            .clip(CircleShape)
            .size(48.dp),
    )
}
```

`clip(CircleShape)` and a default avatar size can be intrinsic; `fillMaxWidth`, screen padding, alignment, and placement usually are not. A modifier on a child does not make the root caller-placeable.

```kotlin
Box(
    modifier = Modifier
        .fillMaxWidth()
        .then(if (selected) Modifier.background(Color.Red) else Modifier),
)
```

```kotlin
fun Modifier.decorateMeasureConstraints(
    decorate: (Constraints) -> Constraints,
): Modifier = layout { measurable, incoming ->
    val constraints = decorate(incoming).constrain(incoming)
    val placeable = measurable.measure(constraints)
    layout(placeable.width, placeable.height) { placeable.placeRelative(0, 0) }
}
```

## Exceptions

- Do not add a modifier to a non-layout `@ReadOnlyComposable` accessor, preview, or test-only single-use composable.
- A private/framework primitive may require `modifier` as its first required parameter.
- Keep an imperative modifier construction when animation/procedural state makes a fluent expression less clear.
- Do not add a root modifier merely because a focused task asks about slots; follow the task scope.

## Related

- [Slot APIs](slot-apis.md) for caller-controlled visual content.
- [Composition contracts](../../compose-performance/references/composition-contracts.md) for read-only accessors.
