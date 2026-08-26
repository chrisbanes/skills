# Kotlin Multiplatform: expect/actual boundaries

## Core principle

Keep common APIs semantic and stable. Put platform mechanics behind small
`expect`/`actual` declarations or interfaces.

## Boundary procedure

1. Name the capability in common terms.
2. Decide whether callers need fakes, injected dependencies, lifecycle ownership,
   or runtime implementation choice.
3. Pick the smallest boundary below and keep the common signature free of
   platform types and vocabulary.
4. Keep business branching in common code; keep actuals and bindings as
   translation layers.
5. Compile every affected source set and test common code with a fake where
   possible. On a platform leak, return to step 1 and rename the capability.

## Choose the boundary

| Situation | Prefer |
|---|---|
| Simple compile-time platform specialization | `expect`/`actual` function, value, typealias, or leaf composable |
| Implementation needs injected dependencies, lifecycle ownership, runtime choice, or test fakes | Common interface plus platform binding |
| UI is mostly shared, one leaf differs | Common composable calling an `expect` leaf |
| Entire screen differs by platform | Separate platform screens behind a common navigation contract |
| Only constants/resources differ | Common API exposing semantic values, actual values per platform |

## Semantic common APIs

```kotlin
// GOOD: common API is semantic
expect fun currentRegion(): Region
```

```kotlin
// BAD: common API leaks Android implementation
expect fun currentRegionFromAndroidLocale(context: Context): Region
```

Actuals may use platform APIs; common callers should not know. If an operation
needs an Activity, view controller, lifecycle owner, DI, or fakes, use a common
interface supplied by platform code instead of an `expect class`:

```kotlin
// commonMain
interface ShareSheet {
    suspend fun shareText(text: String)
}
```

```kotlin
// androidMain
class AndroidShareSheet(
    private val activity: Activity,
) : ShareSheet {
    override suspend fun shareText(text: String) {
        val intent = Intent(Intent.ACTION_SEND)
            .setType("text/plain")
            .putExtra(Intent.EXTRA_TEXT, text)
        activity.startActivity(Intent.createChooser(intent, null))
    }
}
```

The Android implementation is Activity-owned; a generic `Context` often hides
that lifecycle. Define `suspend` precisely (for example, sheet launched versus
sharing completed). Move business rules out of an actual.

Use `expect`/`actual` for simple compile-time specialization. Use an interface
when common code needs fakes, multiple implementations, runtime selection, or
lifecycle ownership:

```kotlin
interface Clipboard {
    suspend fun setText(text: String)
}
```

Platform modules bind `Clipboard` to Android/iOS implementations. Common tests use a fake.

## Shared Compose UI

When shared UI reaches a platform leaf:

1. Keep platform-specific composables at leaf nodes.
2. Pass `Modifier` through every expected composable that emits UI.
3. Reject platform types in `commonMain` signatures (`Context`, `Activity`, Android resource IDs, `Uri`, `Bundle`, `UIViewController`, `NSBundle`, platform permission enums, etc.).
4. Hide native view lifecycle inside the platform actual and use the right interop container (`AndroidView`, `UIKitView`, etc.).
5. Do not launch platform work from a composable body; use remembered,
   lifecycle-aware effects with stable keys inside actual composables.
6. Preview/test the common plain UI composable with fake platform services where possible.

Reject a common platform type, one-platform parameter, broad `Platform` object,
or platform UI high in the tree. If a third platform changes common callers or
common tests require native runtime, return to the boundary choice.

## Related (Compose / shared UI)

Stay focused on platform boundaries in this skill; wire shared UI like any other Compose target:

- [Kotlin control flow](../../kotlin-control-flow/SKILL.md) — keeping common-code business branching explicit with `when`, guard conditions, exhaustiveness, and smart casts.
- [Compose state and effects](../../compose-state-and-effects/SKILL.md) — shared plain UI composables versus state-holder wiring and effect lifecycle.
- [Compose component design](../../compose-component-design/SKILL.md) — reusable shared Compose APIs (modifiers, slots).
