package example

import kotlin.test.Test
import kotlin.test.assertEquals

class CountLabelTest {
  @Test
  fun pluralizesCount() {
    assertEquals("2 items", countLabel(2))
  }
}

private fun countLabel(count: Int) = if (count == 1) "1 item" else "$count items"
