package example

import androidx.compose.animation.AnimatedContent
import androidx.compose.runtime.Composable
import androidx.compose.ui.focus.FocusRequester

@Composable
fun Pane(selectedId: String, requester: FocusRequester) {
  AnimatedContent(selectedId) {
    requester.requestFocus()
    androidx.compose.material.Text(selectedId)
  }
}
