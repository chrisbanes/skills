package example

sealed interface Notice {
    data class Message(val text: String, val urgent: Boolean) : Notice
    data object Empty : Notice
}

fun noticeLabel(notice: Notice): String = when (notice) {
    is Notice.Message -> {
        if (notice.urgent) "urgent:${notice.text}" else notice.text
    }
    Notice.Empty -> "empty"
}
