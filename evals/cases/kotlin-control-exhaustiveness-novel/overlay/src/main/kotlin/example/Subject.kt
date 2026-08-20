package example

sealed interface ApiStatus {
    data class Success(val data: String) : ApiStatus
    data object NetworkError : ApiStatus
    data object Unauthorized : ApiStatus
    data class ValidationError(val reason: String) : ApiStatus
}

fun render(status: ApiStatus): String = when (status) {
    is ApiStatus.Success -> status.data
    ApiStatus.NetworkError -> "offline"
    else -> "failed"
}
