package example

import androidx.compose.material.Text
import androidx.compose.runtime.Composable

enum class SyncStatus { Idle, Syncing, Failed }

@Composable
fun SyncStatusLabel(status: SyncStatus) {
  Text(
    when (status) {
      SyncStatus.Idle -> "Up to date"
      SyncStatus.Syncing -> "Syncing"
      SyncStatus.Failed -> "Sync failed"
    }
  )
}
