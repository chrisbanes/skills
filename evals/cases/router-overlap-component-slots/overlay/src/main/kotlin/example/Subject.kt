package example

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ProfileCard(name: String, modifier: Modifier = Modifier) {
  Column(Modifier.padding(16.dp).then(modifier)) {
    Text(name)
  }
}
