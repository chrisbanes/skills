package example

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Deferred

suspend fun loadTitle(source: Deferred<String>): String =
    try {
        source.await()
    } catch (error: CancellationException) {
        throw error
    } catch (_: Exception) {
        "Untitled"
    }
