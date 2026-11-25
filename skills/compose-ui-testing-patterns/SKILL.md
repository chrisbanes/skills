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
| Text, buttons, conditional content, loading/error states, click/input callbacks | Plain UI Compose test |
| Focus navigation or keyboard behavior | Compose test with key input |
| Visual layout, clipping, elevation, typography, image composition | Screenshot test |
| State holder updates UI correctly | State holder/unit test plus one wiring smoke test |
| Hover, pressed, focused, dragged interaction state | Plain UI test with MutableInteractionSource |
| Navigation, lifecycle, DI integration | Integration test |
| Critical flow that depends on the installed build or crosses an app, process, or OS boundary | Focused device smoke test or end-to-end test, outside this skill |

Keep an existing cheaper regression for the contract it already proves.
For a real permission flow, retain the `createComposeRule` denied-state
assertion and add a device check for the Android dialog and the result the
OS delivers to the app. For R8-sensitive startup, retain the debug integration
test and add startup on the optimized artifact. `StateRestorationTester`
proves the local Compose save-and-restore round trip. Use an installed test
when actual activity callbacks, process death, or OS restoration are part
of the required behavior.

## Plain UI and callback tests

Render the plain composable with controlled state and callbacks. Find nodes by
visible text or semantics. Use a tag when text is absent or ambiguous. Assert
enabled, selected, focused or toggled semantics directly, and use
`assertDoesNotExist` for absence. Capture callback arguments to prove wiring:

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

Assert a plain captured value immediately after the action. Use `runOnIdle`
when the result depends on snapshot state, recomposition or queued work.
Use `waitForIdle` or a bounded `waitUntil` for a real asynchronous condition.
Leave clock auto-advance on unless testing a particular frame. With
`mainClock.autoAdvance = false`, advance to that frame once before its
assertions. Avoid `Thread.sleep`.

## Interaction, keyboard and focus

For hover, press, focus or drag **interaction state**, read the
[interaction-state procedure](references/interaction-state.md) before writing
or reviewing the test. It uses direct, injected interactions.

For **keyboard or D-pad navigation**, send keys and assert focused semantics.
If the composable has no input surface that can change the state, identify the
missing host or parent before proposing a test. For focus graphs, restoration
and key handlers, see [focus navigation](../compose-focus-navigation/SKILL.md).

## Screenshots and images

Use screenshots for visual contracts such as spacing, clipping, typography,
image composition or focus highlights. Fix data, time and animation progress.
Use a local painter or bitmap when appearance matters. When testing which
image was requested, use a fake loader and assert the requested model.

When a named preset or default intentionally changes, keep it in the test and
update its baseline. Keep an explicit fixed value when that geometry is the
contract. Preserve assertions and tolerances unless a separate change justifies
altering them.

For a recording claim, report three checks separately: the actual comparison
result, whether recording wrote the exact output path declared by the test,
and the observed baseline diff. Quote the reported comparison status and
name the literal output path even when absent. A passing comparison can
leave the artifact and baseline untouched. For a findings-only review, stop
at missing evidence. Keep tool-specific commands in the repository runbook.
