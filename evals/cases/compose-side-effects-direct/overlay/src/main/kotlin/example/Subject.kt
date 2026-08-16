package example

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.delay

@Composable
fun TimeoutEffect(onTimeout: () -> Unit) {
  LaunchedEffect(Unit) {
    delay(1_000)
    onTimeout()
  }
}
