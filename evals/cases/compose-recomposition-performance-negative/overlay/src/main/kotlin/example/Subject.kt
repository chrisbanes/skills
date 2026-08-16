package example

import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.offset
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.IntOffset

@Composable
fun FloatingHeader(listState: LazyListState) {
  Box(Modifier.offset { IntOffset(0, listState.firstVisibleItemScrollOffset) })
}
