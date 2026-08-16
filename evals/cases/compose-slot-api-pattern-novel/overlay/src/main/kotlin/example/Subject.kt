package example

import androidx.compose.foundation.layout.Row
import androidx.compose.runtime.Composable

@Composable
fun MessageRow(
  avatar: (@Composable () -> Unit)? = null,
  actions: (@Composable () -> Unit)? = null,
) {
  Row {
    avatar?.invoke()
    androidx.compose.material.Text("message")
    actions?.invoke()
  }
}
