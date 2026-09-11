package example

import kotlin.test.Test

class SubjectTest {
  @Test
  fun rendersWithFixedConfiguration() {
    captureScreenshot(
      width = 480,
      tolerance = 0.02f,
    )
  }
}

private fun captureScreenshot(width: Int, tolerance: Float) = Unit
