package example

sealed interface ScreenState {
    data object Loading : ScreenState
    data class Success(val title: String) : ScreenState
    data class Failure(val message: String) : ScreenState
}

fun screenLabel(state: ScreenState): String = when (state) {
    ScreenState.Loading -> "Loading"
    is ScreenState.Success -> state.title
    else -> "Failed"
}
