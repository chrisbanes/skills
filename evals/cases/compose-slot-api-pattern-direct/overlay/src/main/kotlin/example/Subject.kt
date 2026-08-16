package example

import androidx.compose.foundation.layout.Row
import androidx.compose.material.Icon
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.vector.ImageVector

@Composable
fun ActionRow(title: String, icon: ImageVector) {
  Row {
    Icon(icon, contentDescription = null)
    Text(title)
  }
}
