package example

import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier

@Composable
fun CenteredBadge(modifier: Modifier = Modifier) {
  Box(modifier = modifier, contentAlignment = Alignment.Center) {
    androidx.compose.material.Text("new")
  }
}
