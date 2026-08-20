package example

sealed interface Event {
    data class Message(val text: String, val isUnread: Boolean) : Event
    data object Empty : Event
}

fun rowFor(event: Event): String = when (event) {
    is Event.Message -> {
        if (event.isUnread) "unread:${event.text}" else "read:${event.text}"
    }
    Event.Empty -> "empty"
}
