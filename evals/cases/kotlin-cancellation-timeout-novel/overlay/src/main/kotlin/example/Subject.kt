package example

import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.withTimeout

sealed interface ProfileLoad {
    data class Loaded(val name: String?) : ProfileLoad
    data object TimedOut : ProfileLoad
}

suspend fun loadProfile(timeoutMillis: Long, load: suspend () -> String?): ProfileLoad =
    try {
        withTimeout(timeoutMillis) { ProfileLoad.Loaded(load()) }
    } catch (_: TimeoutCancellationException) {
        ProfileLoad.TimedOut
    }
