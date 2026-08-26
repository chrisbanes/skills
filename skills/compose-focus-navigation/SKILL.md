---
name: compose-focus-navigation
description: Use when writing or reviewing Jetpack Compose UI for TV, keyboard, desktop, accessibility focus, D-pad navigation, FocusRequester, focusProperties, key events, or initial focus behavior.
---

# Compose: focus navigation

## Core principle

Focus is stateful UI behavior: make targets and exceptional edges explicit, then drive and verify it through the user's keyboard, D-pad, or remote input.

## Procedure

1. Start with components that already participate in focus. Add a hook only for a requested behavior:

| Need | Add |
|---|---|
| Normal button/text field/clickable focus | Nothing extra; use the focusable component |
| Programmatic initial/restored focus | `FocusRequester` + `Modifier.focusRequester(...)` |
| Visual or state reaction to focus changes | `Modifier.onFocusChanged { ... }` |
| Custom interactive surface that is not already focusable | `Modifier.focusable()` plus role/semantics as appropriate |

2. Request initial or restored focus from `LaunchedEffect`, keyed to the condition that makes the target present. For lazy content, keep requesters by stable item id and request only after the item is composed.
3. Keep default spatial search unless a concrete edge, jump, or trap is wrong. Encode only those exceptions with `focusProperties`.
4. Handle keys only for behavior that is not normal click or traversal. Consume exactly the handled event; throttle rapid D-pad work at its expensive owner, not across the screen.
5. Restore by semantic identity after refresh: retain the focused id when it exists, otherwise choose a deterministic fallback.
6. Test with key/D-pad input and focused semantics. Use screenshots only for the focus appearance.
7. Finish when all intentional targets and exceptional edges are encoded, loading/refresh behavior has a stable focus policy, and tests use the same input model as users.

For example, request and observe focus only when both behaviors are required:

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

Call focus requests from an effect, not the composable body:

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

Use `focusProperties` only when default spatial search is wrong:

```kotlin
Modifier.focusProperties {
    up = headerRequester
    down = firstRowRequester
    left = FocusRequester.Cancel
}
```

Too many hard-coded links create stale focus graphs. For special key behavior, consume only the handled event:

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

Test focus through user input:

```kotlin
composeTestRule.onNodeWithTag("screen").performKeyInput {
    pressKey(Key.DirectionDown)
}

composeTestRule.onNodeWithTag("play-button").assertIsFocused()
```

Broader test-shape choices are in [Compose UI testing patterns](../compose-ui-testing-patterns/SKILL.md).
