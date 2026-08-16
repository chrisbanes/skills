package example

import androidx.compose.animation.animateColor
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.updateTransition
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

@Composable
fun SelectionTransition(selected: Boolean) {
  val transition = updateTransition(selected, label = "selection")
  val scale = transition.animateFloat(label = "scale") { if (it) 1f else 0.9f }
  val color = transition.animateColor(label = "color") { if (it) Color.Blue else Color.Gray }
  println(scale.value to color.value)
}
