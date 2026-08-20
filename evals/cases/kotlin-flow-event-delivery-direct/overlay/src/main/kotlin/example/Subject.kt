package example

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow

sealed interface Navigation {
    data object Back : Navigation
    data class Profile(val userId: String) : Navigation
}

class NavigationEvents {
    private val mutableEvents = MutableSharedFlow<Navigation>()
    val events: SharedFlow<Navigation> = mutableEvents.asSharedFlow()

    suspend fun send(event: Navigation) {
        mutableEvents.emit(event)
    }
}
