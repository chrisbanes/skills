package example

import androidx.compose.foundation.Canvas
import androidx.compose.runtime.Composable
import androidx.compose.runtime.State
import androidx.compose.ui.Modifier

@Composable
fun ProgressRing(progress: State<Float>) {
  val fraction = progress.value
  RingCanvas(radiusProvider = { fraction * 24f })
}

@Composable
private fun RingCanvas(radiusProvider: () -> Float) {
  Canvas(Modifier) {
    drawCircle(radius = radiusProvider())
  }
}
