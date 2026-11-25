# Filter restoration

The contract is that `FilterChipRow` retains its local `rememberSaveable`
selection when the composable's saved state is written and restored.

```kotlin
val restoration = StateRestorationTester(composeTestRule)
restoration.setContent { FilterChipRow() }
composeTestRule.onNodeWithText("Unread").assertIsNotSelected()
composeTestRule.onNodeWithText("Unread").performClick()
composeTestRule.onNodeWithText("Unread").assertIsSelected()
restoration.emulateSavedInstanceStateRestore()
composeTestRule.onNodeWithText("Unread").assertIsSelected()
```
