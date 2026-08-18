---
name: compose-ui-testing-patterns
description: Use when writing or reviewing Jetpack Compose UI tests, screenshot tests, previews, semantics assertions, fake image loading, keyboard input, focus assertions, interaction state (hover/pressed/focused), or tests for plain state-driven UI composables.
---

# Compose: UI testing patterns

## Core principle

Test the smallest UI contract that proves the behavior. Prefer plain state-driven UI tests with callbacks. Add integration only when lifecycle, navigation, DI, or platform behavior is the thing under test.

## Procedure

1. State the behavior and test concern the task asks you to prove.
2. Inspect the existing test against that concern and choose the smallest
   sufficient seam from the table below.
3. Keep focused edits within the requested test concern. Do not move test-only
   helpers into production or broaden production APIs unless that production
   boundary is itself under test.
4. Drive controlled state or input, synchronize through Compose when needed,
   and assert an observable semantic, visual, or callback result.
5. Finish with no edit when the existing test already uses the narrowest valid
   seam and proves the requested behavior.

## Test target choice

| What you need to prove | Test shape |
|---|---|
| Text, button, loading/error branch, conditional content | Plain UI Compose test |
| Callback wiring from click/input | Plain UI Compose test |
| Focus navigation or keyboard behavior | Compose test with key input |
| Visual layout, clipping, elevation, typography, image composition | Screenshot test |
| State holder updates UI correctly | State holder/unit test plus one wiring smoke test |
| Hover, pressed, focused, dragged interaction state | Plain UI test with MutableInteractionSource |
| Navigation, lifecycle, DI integration | Integration test |

## Prefer plain UI tests

If the screen has a state holder/UI split, test the plain UI composable:

```kotlin
composeTestRule.setContent {
    ProfileScreen(
        state = ProfileUiState(name = "Ada", canSave = true),
        onNameChange = {},
        onSaveClick = { saved = true },
        onBackClick = {},
    )
}

composeTestRule.onNodeWithText("Ada").assertIsDisplayed()
composeTestRule.onNodeWithText("Save").performClick()

assertThat(saved).isTrue()
```

This avoids constructing ViewModels, components, repositories, navigation, and dependency graphs for layout behavior.

## Semantics first

Assert semantics when behavior is semantic:

- Text exists: `onNodeWithText`.
- Button is enabled/disabled: `assertIsEnabled`, `assertIsNotEnabled`.
- Content is selected/focused/toggled: use semantics assertions.
- Content is absent: `assertDoesNotExist`.

Use test tags for nodes that have no stable user-visible text or where multiple nodes share text. Do not use tags as the first choice for all assertions; user-visible semantics are usually stronger.

## Callback testing

Use simple counters or captured values:

```kotlin
var selectedId: String? = null

composeTestRule.setContent {
    ItemList(
        items = listOf(ItemUi("movie-1", "Movie")),
        onItemClick = { selectedId = it },
    )
}

composeTestRule.onNodeWithText("Movie").performClick()

assertThat(selectedId).isEqualTo("movie-1")
```

For plain captured callback values, a direct assertion after the action is usually enough. Use `runOnIdle` when the assertion needs Compose to finish applying snapshot state, recomposition, or queued UI work before reading the result.

## Keep UI tests deterministic

For layout, branch, and callback behavior, render controlled state with `setContent` instead of constructing the production app graph. Production DI, repositories, lifecycle observers, and background effects add asynchronous work that is irrelevant to a plain UI contract and can make the test flaky.

Do not use `Thread.sleep` to wait for Compose. Drive the UI to a known state, then use semantic assertions and Compose synchronization (`waitForIdle`, `runOnIdle`, or a bounded `waitUntil` for a real asynchronous condition). Reserve full-app integration for behavior that actually depends on navigation, lifecycle, DI, or platform wiring.

## Interaction state with MutableInteractionSource

When a composable's appearance or behavior depends on interaction state (hover, focus, press, drag), inject a `MutableInteractionSource` and emit the desired state directly. Do not try to simulate pointer/mouse events to trigger interaction states — that approach is fragile, environment-dependent, and produces flaky tests.

```kotlin
val interactionSource = MutableInteractionSource()

composeTestRule.setContent {
    OutlinedButton(
        onClick = {},
        interactionSource = interactionSource,
    )
}

// Assert default (un-hovered) state
composeTestRule.onNodeWithText("OutlinedButton").assertIsDisplayed()

// Emit hover — interactionSource.emit is a suspend function,
// so call it from a test coroutine scope.
TestScope().launch {
    interactionSource.emit(HoverInteraction.Enter())
}

composeTestRule.waitForIdle()

// Assert the visual/semantic change that hover produces
// (e.g., border color, elevation, or capture for screenshot test)
composeTestRule.onNodeWithText("OutlinedButton").assertIsDisplayed()
```

The same pattern works for `PressInteraction.Press` / `Release` / `Cancel`, `FocusInteraction.Focus` / `Unfocus`, and `DragInteraction.Start` / `Stop` / `Cancel`. Emit the entry interaction, `waitForIdle`, then assert the result.

Key points:

- **Always inject `MutableInteractionSource`** rather than relying on the default internal source. This gives you full control over state transitions.
- **Emit interactions from a coroutine scope** (e.g. `TestScope().launch { }`) since `emit` is a suspend function. Do not use `LaunchedEffect` — that is a production Compose effect, not a test tool.
- **Assert the *result* of the interaction** (visual change, semantic change, enabled state), not the interaction itself. The interaction source is a test *driver*, not the assertion target.
- **Use this for screenshot tests too** — emit the interaction state, then capture the screenshot for a deterministic hover/press/focus visual.

## Keyboard and focus

For keyboard, TV, and desktop UI, drive navigation with the same input model users use (keys/D-pad), not clicks alone. Assert focused semantics, not colors or scale; reserve screenshots for visual focus treatment.

Details—focus graph, `FocusRequester`, restoration, key handlers, and test patterns: [`compose-focus-navigation`](../compose-focus-navigation/SKILL.md).

## Screenshot tests

Use screenshots for visual contracts that semantics cannot prove:

- Layout spacing/alignment.
- Themed colors, typography, elevation, shadows.
- Image composition, gradients, overlays.
- Focus highlight appearance.
- Loading skeletons or dense visual states.

Keep screenshot state deterministic:

- Use fixed state data.
- Freeze clocks or animation progress when possible.
- Replace network/image loading with fake or preview handlers.
- Avoid asserting dynamic text such as current time unless controlled.

## Fake images and platform services

When image content is irrelevant, fake the loader and assert the requested model if that is the behavior. The exact hook depends on your image library; a project helper might look like this:

```kotlin
val requestedModels = mutableListOf<Any?>()

// Example helper, not a Compose API.
setContentWithFakeImageLoader { request ->
    requestedModels += request.data
    errorPainter()
}
```

When image appearance matters, provide a deterministic local painter/bitmap instead of network data.

## Common mistakes

| Mistake | Fix |
|---|---|
| Constructing full app graph to test an error row | Test plain UI with `state = Error` |
| Testing click behavior through a ViewModel mock | Pass a callback and assert it was invoked |
| Screenshot test for simple text presence | Use semantics assertion |
| Semantics test for padding/color/focus ring | Use screenshot test |
| Test tags everywhere | Prefer text/content description/role when stable |
| UI test depends on real image loading/network/time | Fake or freeze the source |
| Sleeping after an action before asserting UI | Use semantics plus `waitForIdle`, `runOnIdle`, or bounded `waitUntil` |
| Production DI or app wiring for a state/rendering assertion | Render controlled state with `setContent`; use integration only when that wiring is under test |
| Simulating hover/press/focus with mouse or touch events | Inject `MutableInteractionSource` and emit the interaction |
| Relying on the default `InteractionSource` in tests | Pass `MutableInteractionSource` so you can control state |
| TV/keyboard UI tested with `performClick` only | Use key input and focus assertions; see [compose-focus-navigation](../compose-focus-navigation/SKILL.md) |

## Red flags during review

- "This UI test is flaky because images load slowly."
- A test uses production DI for simple rendering.
- A screenshot has random dates, clocks, remote images, or live data.
- Assertions only check that a node exists after performing an action, not that the callback/state change happened.
- Focus behavior is visually inspected but not asserted.
- A test uses `performMouseInput` or touch injection to trigger hover/press states instead of `MutableInteractionSource.emit`.
- A composable accepts `interactionSource` but tests don't inject `MutableInteractionSource`.
- A plain rendering test starts the production app or uses `Thread.sleep` before asserting.

## RED/GREEN agent scenarios

1. RED launches a production app, waits with `Thread.sleep`, and only asserts that a node exists. GREEN renders fixed state with `setContent`, drives the action, synchronizes through Compose, and asserts the semantic state or callback result.
2. Novel case: a screen's repository-backed state holder starts background work, but the test only needs to prove a disabled Save button. GREEN tests the plain UI state directly; a separate integration test covers the state-holder wiring if needed.
3. Counterexample: navigation behavior depends on a real `NavController` lifecycle. GREEN uses an integration test rather than pretending a plain rendering test proves that contract.
4. Focused counterexample: a value-only formatter test already uses a plain unit
   test and the task asks only whether it needs a UI harness. GREEN leaves the
   test-local helper and workspace unchanged.
