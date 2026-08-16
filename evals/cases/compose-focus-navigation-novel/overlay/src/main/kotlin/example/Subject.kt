package example

import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester

@Composable
fun Catalog() {
  val requester = remember { FocusRequester() }
  requester.requestFocus()
  Box(Modifier.focusRequester(requester))
}
