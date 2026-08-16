package example

import kotlinx.collections.immutable.ImmutableList

data class FeedState(
  val items: ImmutableList<String>,
)
