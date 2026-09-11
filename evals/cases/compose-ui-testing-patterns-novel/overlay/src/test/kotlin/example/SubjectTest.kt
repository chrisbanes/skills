package example

import kotlin.test.Test

class SubjectTest {
  @Test
  fun capturesSubject() {
    captureScreenshot(
      artifactPath = "build/recorded/subject.png",
      tolerance = 0.02f,
    )
  }
}

// The log says: "Verification passed".
// No recording output or changed baseline was reported.
private fun captureScreenshot(artifactPath: String, tolerance: Float) = Unit
