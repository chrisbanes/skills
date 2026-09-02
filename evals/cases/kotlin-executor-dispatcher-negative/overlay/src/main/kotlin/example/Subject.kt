package example

import java.io.Closeable
import java.util.concurrent.Executors
import kotlinx.coroutines.ExecutorCoroutineDispatcher
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.withContext

class CodecWorker : Closeable {
    private val dispatcher: ExecutorCoroutineDispatcher =
        Executors.newSingleThreadExecutor().asCoroutineDispatcher()

    suspend fun <T> onCodecThread(block: () -> T): T =
        withContext(dispatcher) { block() }

    override fun close() {
        dispatcher.close()
    }
}
