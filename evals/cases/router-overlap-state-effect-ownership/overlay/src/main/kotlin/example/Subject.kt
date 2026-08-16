package example

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.flow.Flow

class ScreenModel {
  var query: String = ""
}

@Composable
fun SearchScreen(model: ScreenModel, events: Flow<String>, navigate: (String) -> Unit) {
  LaunchedEffect(Unit) { events.collect(navigate) }
  androidx.compose.material.Text(model.query)
}
