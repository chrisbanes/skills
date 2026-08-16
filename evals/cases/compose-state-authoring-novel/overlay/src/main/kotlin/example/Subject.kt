package example

import androidx.compose.runtime.Composable
import androidx.compose.runtime.ReadOnlyComposable
import androidx.compose.runtime.compositionLocalOf

val LocalCounter = compositionLocalOf { androidx.compose.runtime.mutableStateOf(0) }

@Composable
@ReadOnlyComposable
fun currentBadgeCount(): Int = LocalCounter.current.value
