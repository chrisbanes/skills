---
name: compose-focus-navigation
description: Use when writing or reviewing Jetpack Compose UI for TV, keyboard, desktop, accessibility focus, D-pad navigation, FocusRequester, focusProperties, key events, or initial focus behavior.
---

# Compose: focus navigation

## Core principle

Focus is stateful UI behavior. Make focus targets explicit, request focus after composition succeeds, and test navigation with the same input model users use: keyboard, D-pad, or remote keys.

## When to use this skill

Use this when UI:

- Runs on TV, desktop, ChromeOS, keyboard-first Android, or remote-control devices.
- Uses `FocusRequester`, `focusRequester`, `focusProperties`, `onFocusChanged`, or key handlers.
- Needs initial focus, restored focus, directional navigation, or back/escape behavior.
- Has a carousel, grid, lazy list, menu, dialog, or modal with focus traps.
- Has tests asserting which item is focused.

## Build focus targets deliberately

Start with components that already participate in focus, then add only the focus hooks the behavior needs:

| Need | Add |
|---|---|
| Normal button/text field/clickable focus | Nothing extra; use the focusable component |
| Programmatic initial/restored focus | `FocusRequester` + `Modifier.focusRequester(...)` |
| Visual or state reaction to focus changes | `Modifier.onFocusChanged { ... }` |
| Custom interactive surface that is not already focusable | `Modifier.focusable()` plus role/semantics as appropriate |

For example, request and observe focus only when both behaviors are needed:

```kotlin
val requester = remember { FocusRequester() }

Button(
    onClick = onClick,
    modifier = Modifier
        .focusRequester(requester)
        .onFocusChanged { state -> isFocused = state.isFocused },
) {
    Text("Play")
}
```

Prefer focusable components (`Button`, `TextField`, clickable/selectable surfaces) over manually adding `focusable()` to passive layout. Add manual focus only when the element is truly interactive or participates in navigation.

## Request focus after composition

Call focus requests from an effect, not from the composable body:

```kotlin
val initialFocus = remember { FocusRequester() }

LaunchedEffect(initialFocus) {
    initialFocus.requestFocus()
}
```

If the target appears after loading, key the request to the condition:

```kotlin
LaunchedEffect(items.isNotEmpty()) {
    if (items.isNotEmpty()) {
        firstItemRequester.requestFocus()
    }
}
```

For lazy content, request focus only after the item is actually composed. Keep requesters in stable item state keyed by item id, not by index alone if the list can reorder.

## Directional navigation

Use `focusProperties` when default spatial search is wrong:

```kotlin
Modifier.focusProperties {
    up = headerRequester
    down = firstRowRequester
    left = FocusRequester.Cancel
}
```

Use this sparingly. Too many hard-coded links create stale focus graphs when layouts change. Prefer natural focus order unless the design requires a specific jump or trap.

## Key events

Use key handlers for behavior that is not normal click/focus traversal:

```kotlin
Modifier.onPreviewKeyEvent { event ->
    if (event.type == KeyEventType.KeyUp && event.key == Key.Back) {
        onBack()
        true
    } else {
        false
    }
}
```

Return `true` only when consumed. Returning `true` too broadly breaks text entry, accessibility shortcuts, and parent navigation.

For rapid D-pad input, throttle at the boundary that owns the expensive behavior (for example row scrolling or paging), not globally across the whole screen.

## Focus restoration

Preserve focus by semantic identity:

- Track selected/focused item id, not just index.
- Use stable `key` values in lazy lists and grids.
- When content refreshes, re-request focus for the same id if it still exists.
- If it no longer exists, choose a deterministic fallback: nearest neighbor, first item, or parent container.

## Common mistakes

| Mistake | Fix |
|---|---|
| Adding `focusRequester` and `onFocusChanged` to every button | Add them only when requesting or observing focus |
| `requestFocus()` in the composable body | Move to `LaunchedEffect` |
| Initial focus keyed to `Unit` while target appears later | Key to loaded/visible condition |
| Focus requesters stored by lazy list index | Store by stable item id |
| Everything gets custom `focusProperties` | Let spatial search work; override only broken edges |
| Key handler returns `true` for all keys | Consume only handled keys |
| Tests click nodes in TV/D-pad UI | Send key input and assert focus |

## Testing

Test focus through user input:

```kotlin
composeTestRule.onNodeWithTag("screen").performKeyInput {
    pressKey(Key.DirectionDown)
}

composeTestRule.onNodeWithTag("play-button").assertIsFocused()
```

Prefer asserting focused semantics over visual styling. Use screenshot tests only for focus appearance, not for deterministic focus ownership.

Broader test-shape choices (plain UI vs integration, semantics-first): [`compose-ui-testing-patterns`](../compose-ui-testing-patterns/SKILL.md).

## Red flags during review

- "It focuses correctly when I tap it" for a keyboard/TV UI.
- Initial focus works only with fixed data and fails after loading/refresh.
- Focus state is inferred from selected data state when focus and selection are different concepts.
- The focus graph is described in comments but not encoded or tested.
