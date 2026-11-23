# Filter restoration

The contract is that `FilterChipRow` retains its local `rememberSaveable`
selection when the composable's saved state is written and restored.

```kotlin
val restoration = StateRestorationTester(composeTestRule)
restoration.setContent { FilterChipRow() }
composeTestRule.onNodeWithText("Unread").performClick()
restoration.emulateSavedInstanceStateRestore()
composeTestRule.onNodeWithText("Unread").assertIsSelected()
```
