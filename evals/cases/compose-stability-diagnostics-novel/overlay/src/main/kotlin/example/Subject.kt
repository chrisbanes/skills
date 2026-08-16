package example

import androidx.compose.runtime.Stable

@Stable
class ProfilingScenario(
  var phase: Int,
  val samples: MutableList<Float>,
)
