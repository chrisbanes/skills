# Interaction state tests

When a composable's appearance or behavior depends on hover, focus, press, or
drag, inject a `MutableInteractionSource` and emit the desired state directly.
Do not simulate pointer or mouse events: that is environment-dependent and
flaky.

```kotlin
val interactionSource = MutableInteractionSource()

composeTestRule.setContent {
    OutlinedButton(
        onClick = {},
        interactionSource = interactionSource,
    )
}

composeTestRule.onNodeWithText("OutlinedButton").assertIsDisplayed()

TestScope().launch {
    interactionSource.emit(HoverInteraction.Enter())
}
composeTestRule.waitForIdle()
composeTestRule.onNodeWithText("OutlinedButton").assertIsDisplayed()
```

The same pattern applies to `PressInteraction.Press` / `Release` / `Cancel`,
`FocusInteraction.Focus` / `Unfocus`, and `DragInteraction.Start` / `Stop` /
`Cancel`: emit the entry interaction, wait for idle, then assert its result.

- Always inject `MutableInteractionSource`, never rely on its internal default.
- Emit from a coroutine scope, such as `TestScope().launch { }`, because `emit`
  is suspend. Do not use production `LaunchedEffect` as a test tool.
- Assert the observable visual, semantic, or enabled-state result, not the
  interaction object. The source drives the test; it is not the assertion.
- For screenshots, emit the state before capture for deterministic
  hover/press/focus visuals.
