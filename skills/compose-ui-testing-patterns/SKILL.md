---
name: compose-ui-testing-patterns
description: Use when writing or reviewing Jetpack Compose UI tests, screenshot tests, previews, semantics assertions, fake image loading, keyboard input, focus assertions, or tests for plain state-driven UI composables.
---

# Compose: UI testing patterns

## Core principle

Test the smallest UI contract that proves the behavior. Prefer plain state-driven UI tests with callbacks. Add integration only when lifecycle, navigation, DI, or platform behavior is the thing under test.

## Test target choice

| What you need to prove | Test shape |
|---|---|
| Text, button, loading/error branch, conditional content | Plain UI Compose test |
| Callback wiring from click/input | Plain UI Compose test |
| Focus navigation or keyboard behavior | Compose test with key input |
| Visual layout, clipping, elevation, typography, image composition | Screenshot test |
| State holder updates UI correctly | State holder/unit test plus one wiring smoke test |
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
| TV/keyboard UI tested with `performClick` only | Use key input and focus assertions; see [compose-focus-navigation](../compose-focus-navigation/SKILL.md) |

## Red flags during review

- "This UI test is flaky because images load slowly."
- A test uses production DI for simple rendering.
- A screenshot has random dates, clocks, remote images, or live data.
- Assertions only check that a node exists after performing an action, not that the callback/state change happened.
- Focus behavior is visually inspected but not asserted.
