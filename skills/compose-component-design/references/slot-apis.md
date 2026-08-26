# Compose slot API pattern

## Core principle

A reusable component owns layout structure; callers provide unconstrained visual content through slots.

## Procedure

1. Confirm the component is reusable and identify the regions that vary by caller.
2. Replace unconstrained primitive content and shape flags with named `@Composable` slots. Retain parameters that enforce semantic, design-system, constrained-type, or measured fast-path contracts.
3. Make an optional slot nullable with a `null` default so its container and spacing can disappear.
4. Add a `RowScope`, `ColumnScope`, or `BoxScope` receiver only when caller control of that region's child layout is a public contract; an internal layout alone is not enough.
5. Put repeated composable defaults and tokens in `XxxDefaults`.
6. Pair this with [Modifier and layout](modifier-layout.md) only when root placement is in scope.
7. Finish when callers can supply variable content without a flag matrix, while the component's own semantic and layout invariants remain explicit.

```kotlin
@Composable
fun SettingsRow(
    headlineContent: @Composable () -> Unit,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    supportingContent: (@Composable () -> Unit)? = null,
    leadingContent: (@Composable () -> Unit)? = null,
    trailingContent: (@Composable () -> Unit)? = null,
) { /* component-owned structure */ }
```

Use `xxxContent` for free-form slots, or a semantic noun for a deliberately constrained region. Keep one naming convention within a component. For a public action region whose children deliberately control a row's allocation, use a scope receiver:

```kotlin
fun MyTopBar(
    title: @Composable () -> Unit,
    actions: @Composable RowScope.() -> Unit = {},
)
```

An ordinary trailing slot inside a component-owned `Row` remains `@Composable () -> Unit`: callers choose content, while the component owns order and spacing.

## Exceptions

- A true single-use helper, preview, or test fixture can keep primitive parameters and inline content.
- Keep a primitive when every caller must share a fixed semantic/design-system contract, or when it is a real constrained value such as `checked`.
- In a measured hot path, retain primitives when a slot allocation is proven to matter.
- Do not make a scope receiver or slot merely to anticipate hypothetical flexibility.

## Related

[Modifier and layout](modifier-layout.md) covers caller placement; slots cover caller content.
