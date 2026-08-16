package example

import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.onGloballyPositioned

@Composable
fun MeasuredCard() {
  var width by remember { mutableStateOf(0) }
  Box(Modifier.onGloballyPositioned { width = it.size.width }) {
    androidx.compose.material.Text("width=$width")
  }
}
