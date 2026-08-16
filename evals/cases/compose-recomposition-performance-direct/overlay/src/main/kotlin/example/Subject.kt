package example

import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.layout.offset

@Composable
fun FloatingHeader(listState: LazyListState) {
  val offset = listState.firstVisibleItemScrollOffset
  Box(Modifier.offset(y = offset.dp))
}
