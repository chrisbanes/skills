package example

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow

sealed interface Route {
    data object Back : Route
    data class Profile(val userId: String) : Route
}

class RouteEvents {
    private val mutableRoutes = MutableSharedFlow<Route>()
    val routes: SharedFlow<Route> = mutableRoutes.asSharedFlow()
}

fun routeLabel(route: Route): String = when (route) {
    Route.Back -> "Back"
    else -> "Profile"
}
