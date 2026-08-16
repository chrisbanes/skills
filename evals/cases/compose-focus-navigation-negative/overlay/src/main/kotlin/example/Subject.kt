package example

import androidx.compose.material.Button
import androidx.compose.material.Text
import androidx.compose.runtime.Composable

@Composable
fun SaveButton(onSave: () -> Unit) {
  Button(onClick = onSave) {
    Text("Save")
  }
}
