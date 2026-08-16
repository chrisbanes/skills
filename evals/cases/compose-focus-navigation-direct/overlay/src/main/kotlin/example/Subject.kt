package example

import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester

@Composable
fun SearchInput() {
  val requester = FocusRequester()
  Box(Modifier.focusRequester(requester))
}
