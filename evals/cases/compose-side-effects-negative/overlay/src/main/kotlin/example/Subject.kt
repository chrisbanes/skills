package example

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.rememberUpdatedState

@Composable
fun ScreenAnalytics(screenId: String, send: (String) -> Unit) {
  val currentSend = rememberUpdatedState(send)
  LaunchedEffect(screenId) {
    currentSend.value(screenId)
  }
}
