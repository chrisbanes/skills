package example

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

@Composable
fun DetailsCard(expanded: Boolean, modifier: Modifier = Modifier) {
  if (expanded) {
    Column(modifier) { androidx.compose.material.Text("details") }
  } else {
    Box { androidx.compose.material.Text("summary") }
  }
}
