package example

import androidx.test.core.app.ActivityScenario
import kotlin.test.Test

class SearchFieldTest {
  @Test
  fun entersQuery() {
    ActivityScenario.launch(MainActivity::class.java)
  }
}
