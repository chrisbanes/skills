package example

import kotlin.test.Test

class UserInputTest {
  @Test
  fun sendMessage() {
    launchProductionApplication()
    Thread.sleep(2_000)
    findNode("message-input").typeText("hello")
    findNode("send").click()
  }
}

private fun launchProductionApplication() = Unit
private fun findNode(tag: String) = FakeNode()
private class FakeNode {
  fun typeText(value: String) = Unit
  fun click() = Unit
}
