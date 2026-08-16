package example

import androidx.compose.animation.core.Animatable
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer

@Composable
fun FadingCard(alpha: Animatable<Float, *>) {
  Box(Modifier.graphicsLayer { this.alpha = alpha.value })
}
