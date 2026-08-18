package example

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalDensity

@Composable
fun MatchedRows() {
  var anchorHeightPx by remember { mutableIntStateOf(0) }
  val density = LocalDensity.current
  Column {
    Box(Modifier.onSizeChanged { anchorHeightPx = it.height })
    Box(Modifier.height(with(density) { anchorHeightPx.toDp() }))
  }
}
