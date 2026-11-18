package example

import kotlinx.coroutines.Deferred
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive

suspend fun loadTitle(source: Deferred<String>): String =
    runCatching { source.await() }.getOrElse {
        currentCoroutineContext().ensureActive()
        "Untitled"
    }
