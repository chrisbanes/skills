package example

fun statusLabel(serverStatus: String): String = when (serverStatus) {
    "ready" -> "Ready"
    "paused" -> "Paused"
    else -> "Unknown: $serverStatus"
}
