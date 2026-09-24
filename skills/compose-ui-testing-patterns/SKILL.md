---
name: compose-ui-testing-patterns
description: Use when writing or reviewing Jetpack Compose UI tests, screenshot tests or baseline-recording evidence, previews, semantics assertions, fake image loading, keyboard input, focus assertions, interaction state (hover/pressed/focused), or tests for plain state-driven UI composables.
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

When interaction state is the concern, read
[the interaction-state procedure](references/interaction-state.md) completely
before writing or reviewing the test. It requires direct, injected interaction
state rather than fragile pointer simulation.

## Keyboard and focus

For keyboard, TV, and desktop UI, drive navigation with the same input model users use (keys/D-pad), not clicks alone. Assert focused semantics, not colors or scale; reserve screenshots for visual focus treatment.
If the inspected composable exposes no input surface that can change the state,
name the missing host or parent interaction seam before proposing a key-driven
test; do not assume a selector or control exists in the supplied UI.

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

### When screenshot defaults change

- Keep an intentionally changed named preset or default in the test and update
  its baseline. Do not substitute a raw value to retain the old image; preserve
  assertions and tolerances unless independently justified.
- Keep an explicit fixed value when that fixed resolution or geometry is the
  contract.
- Verify recording separately from comparison: inspect the expected artifact
  paths and intentional baseline diff. Read the exact output path from the test,
  confirm that artifact exists, and name that literal path in the verification
  evidence. When a verification log reports a pass, state what passed and then
  check recording independently; a passing comparison does not prove that
  recording wrote the artifact. If the artifact or baseline diff is
  unavailable, report that gap rather than claiming recording succeeded. Keep
  tool-specific commands in the repository runbook.

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
