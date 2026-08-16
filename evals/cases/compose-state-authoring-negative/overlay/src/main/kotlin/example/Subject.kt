package example

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.setValue

class CounterState {
  var count by mutableIntStateOf(0)
    private set

  fun increment() {
    count += 1
  }
}
