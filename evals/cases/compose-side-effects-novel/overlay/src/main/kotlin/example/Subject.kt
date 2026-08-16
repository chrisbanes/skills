package example

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.flow.Flow

@Composable
fun NavigationEvents(events: Flow<String>, navigate: (String) -> Unit) {
  LaunchedEffect(Unit) {
    events.collect { route -> navigate(route) }
  }
}
