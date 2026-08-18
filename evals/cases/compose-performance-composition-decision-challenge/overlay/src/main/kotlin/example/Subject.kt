package example

import androidx.compose.runtime.Composable
import androidx.compose.runtime.State

@Composable
fun SearchResults(results: State<List<String>>) {
  if (results.value.isEmpty()) {
    EmptyResults()
  } else {
    ResultList(results.value)
  }
}

@Composable
private fun EmptyResults() = Unit

@Composable
private fun ResultList(items: List<String>) = Unit
