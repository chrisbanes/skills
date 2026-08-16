package example

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue

class CounterState {
  var count by mutableStateOf(0)

  fun increment() {
    count += 1
  }
}
