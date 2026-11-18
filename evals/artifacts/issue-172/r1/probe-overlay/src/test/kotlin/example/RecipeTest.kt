package example

import androidx.compose.animation.core.animateDp
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.updateTransition
import androidx.compose.foundation.interaction.HoverInteraction
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsHoveredAsState
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.OutlinedButton
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.Layout
import androidx.compose.ui.layout.layout
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.constrain
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

private enum class Phase { Hidden, Visible }

@Composable
private fun TransitionRecipe(phase: Phase) {
    val transition = updateTransition(targetState = phase, label = "phase")
    val alpha by transition.animateFloat(label = "alpha") { target ->
        if (target == Phase.Visible) 1f else 0f
    }
    val offset by transition.animateDp(label = "offset") { target ->
        if (target == Phase.Visible) 0.dp else 24.dp
    }
    Text("$alpha, $offset")
}

@Composable
fun HoverButton(interactionSource: MutableInteractionSource) {
    val hovered by interactionSource.collectIsHoveredAsState()
    OutlinedButton(onClick = {}, interactionSource = interactionSource) {
        Text(if (hovered) "Hovered" else "Hover me")
    }
}

class HoverRecipeTest {
    @get:Rule val composeTestRule = createComposeRule()

    @Test fun changesTextOnHover() {
        val interactionSource = MutableInteractionSource()

        composeTestRule.setContent {
            HoverButton(interactionSource)
        }

        composeTestRule.onNodeWithText("Hover me").assertIsDisplayed()

        runBlocking {
            interactionSource.emit(HoverInteraction.Enter())
        }
        composeTestRule.waitForIdle()
        composeTestRule.onNodeWithText("Hovered").assertIsDisplayed()
    }
}

fun Modifier.decorateMeasureConstraints(
    decorate: (Constraints) -> Constraints,
): Modifier = layout { measurable, incoming ->
    val constraints = incoming.constrain(decorate(incoming))
    val placeable = measurable.measure(constraints)
    layout(placeable.width, placeable.height) { placeable.placeRelative(0, 0) }
}

class ConstraintsRecipeTest {
    @get:Rule val composeTestRule = createComposeRule()

    @Test fun clampsOversizedRequest() = checkMeasurement(200, 100)

    @Test fun preservesInRangeRequest() = checkMeasurement(60, 60)

    private fun checkMeasurement(requested: Int, expected: Int) {
        var received: Constraints? = null
        var measuredHeight: Int? = null
        val incoming = Constraints(maxWidth = 100, maxHeight = 100)
        composeTestRule.setContent {
            Layout(content = {
                Layout(
                    content = {},
                    modifier = Modifier.decorateMeasureConstraints {
                        it.copy(minHeight = requested, maxHeight = requested)
                    },
                ) { _, childConstraints ->
                    received = childConstraints
                    layout(0, childConstraints.minHeight) {}
                }
            }) { measurables, _ ->
                val child = measurables.single().measure(incoming)
                measuredHeight = child.measuredHeight
                layout(child.width, child.height) { child.placeRelative(0, 0) }
            }
        }
        composeTestRule.runOnIdle {
            assertEquals(incoming.copy(minHeight = expected, maxHeight = expected), received)
            assertEquals(expected, measuredHeight)
            assertTrue(measuredHeight!! in incoming.minHeight..incoming.maxHeight)
        }
    }
}

private data class Item(val id: String)

@Composable
private fun RowCard(onClick: () -> Unit) {
    OutlinedButton(onClick = onClick) { Text("Click") }
}

@Composable
private fun ItemsRecipe(list: List<Item>, onItemClick: (String) -> Unit) {
    LazyColumn {
        items(list, key = { it.id }) { item ->
            val onClick = remember(item.id, onItemClick) { { onItemClick(item.id) } }
            RowCard(onClick = onClick)
        }
    }
}

@Composable
private fun MergedRecipe(parent: Map<String, String>, overlay: Map<String, String>) {
    val merged = parent + overlay
    Text(merged.getValue("value"))
}

class RememberedRecipeTest {
    @get:Rule val composeTestRule = createComposeRule()

    @Test fun sameItemInvokesReplacementHandler() {
        val calls = mutableListOf<String>()
        val handler = mutableStateOf<(String) -> Unit>({ calls.add("old:$it") })
        val items = listOf(Item("same-id"))
        composeTestRule.setContent { ItemsRecipe(items, handler.value) }
        composeTestRule.onNodeWithText("Click").assertIsDisplayed()

        composeTestRule.runOnIdle { handler.value = { calls.add("new:$it") } }
        composeTestRule.onNodeWithText("Click").performClick()
        composeTestRule.runOnIdle { assertEquals(listOf("new:same-id"), calls) }
    }

    @Test fun snapshotMapChangesAndImmutableReplacementsUpdateMergedText() {
        val parent = mutableStateOf<Map<String, String>>(mapOf("value" to "parent"))
        val overlay = mutableStateMapOf<String, String>()
        composeTestRule.setContent { MergedRecipe(parent.value, overlay) }
        composeTestRule.onNodeWithText("parent").assertIsDisplayed()

        composeTestRule.runOnIdle { overlay["value"] = "overlay" }
        composeTestRule.onNodeWithText("overlay").assertIsDisplayed()

        composeTestRule.runOnIdle { overlay["value"] = "changed in place" }
        composeTestRule.onNodeWithText("changed in place").assertIsDisplayed()

        composeTestRule.runOnIdle { overlay.clear() }
        composeTestRule.onNodeWithText("parent").assertIsDisplayed()

        composeTestRule.runOnIdle { parent.value = mapOf("value" to "replacement") }
        composeTestRule.onNodeWithText("replacement").assertIsDisplayed()
    }
}
