package example

import androidx.compose.animation.AnimatedContent
import androidx.compose.material.Text
import androidx.compose.runtime.Composable

data class Message(val id: Long, val title: String)

@Composable
fun MessageSwap(message: Message) {
  AnimatedContent(targetState = message.id) {
    Text(message.title)
  }
}
