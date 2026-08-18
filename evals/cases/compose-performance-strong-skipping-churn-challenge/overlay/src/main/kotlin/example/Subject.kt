package example

import androidx.compose.runtime.Composable

data class FeedUiState(
  val items: List<String>,
)

@Composable
fun FeedRoute(items: List<String>) {
  FeedContent(FeedUiState(items = items.toList()))
}

@Composable
private fun FeedContent(state: FeedUiState) = Unit
