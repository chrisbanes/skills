package example

import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.ui.focus.FocusRequester

class ConversationViewModel {
  val listState = LazyListState()
  val inputFocus = FocusRequester()
  var draft: String = ""
}
