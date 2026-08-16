package example

import androidx.compose.material.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

@Composable
fun SearchContent() {
  var query by remember { mutableStateOf("") }
  TextField(value = query, onValueChange = { query = it })
}
