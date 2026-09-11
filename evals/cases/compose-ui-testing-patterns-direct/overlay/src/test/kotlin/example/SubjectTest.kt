package example

import kotlin.test.Test

class SubjectTest {
  @Test
  fun rendersWithDefaultConfiguration() {
    captureScreenshot(
      options = CaptureOptions.Fixed(width = 480),
      tolerance = 0.02f,
    )
  }
}

private object CaptureOptions {
  object Default
  fun Fixed(width: Int) = Unit
}
private fun captureScreenshot(options: Any, tolerance: Float) = Unit
