package example

import java.util.concurrent.BlockingQueue
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext

class WorkQueue(private val dispatcher: CoroutineDispatcher) {
    suspend fun take(queue: BlockingQueue<String>): String =
        withContext(dispatcher) { queue.take() }
}
