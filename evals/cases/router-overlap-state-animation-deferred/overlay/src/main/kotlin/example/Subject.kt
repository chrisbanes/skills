package example

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.material.Text
import androidx.compose.runtime.Composable

class HeaderViewModel {
  val listState = LazyListState()
}

@Composable
fun Header(model: HeaderViewModel) {
  val visible = model.listState.firstVisibleItemScrollOffset < 20
  AnimatedVisibility(visible) { Text("Header") }
}
