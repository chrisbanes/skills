package example

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.material.Text
import androidx.compose.runtime.Composable

@Composable
fun Selection(current: String?) {
  AnimatedVisibility(visible = current != null) {
    Text(current!!)
  }
}
