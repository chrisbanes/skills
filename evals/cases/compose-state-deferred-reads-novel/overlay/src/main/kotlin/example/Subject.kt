package example

import androidx.compose.foundation.Canvas
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.onSizeChanged

@Composable
fun FadingCircle(progress: () -> Float) {
  var width by remember { mutableStateOf(0) }
  val radius = width * progress()
  Canvas(Modifier.onSizeChanged { width = it.width }) {
    drawCircle(radius = radius)
  }
}
