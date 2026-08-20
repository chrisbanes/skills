package example

data class UserId(val value: String)

fun profilePath(userId: UserId): String = "/users/${userId.value}"
