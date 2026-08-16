package example

import androidx.compose.runtime.Composable

data class RowModel(val tags: MutableList<String>)

@Composable
fun Row(model: RowModel) {
  androidx.compose.material.Text(model.tags.joinToString())
}
