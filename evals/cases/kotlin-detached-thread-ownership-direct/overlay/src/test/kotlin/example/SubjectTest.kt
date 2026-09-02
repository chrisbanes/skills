package example

import java.nio.file.Path
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertTrue

class SubjectTest {
    @Test
    fun evictionCompletesOnSuppliedDispatcher() = runBlocking {
        val executionThread = AtomicReference<String>()
        val completed = CountDownLatch(1)
        val executor = Executors.newSingleThreadExecutor { task ->
            Thread(task, "disk-cache")
        }
        executor.asCoroutineDispatcher().use { dispatcher ->
            DiskCache(Path.of("cache"), dispatcher) {
                executionThread.set(Thread.currentThread().name)
                completed.countDown()
            }.evictExpired()
        }

        assertTrue(completed.await(1, TimeUnit.SECONDS))
        assertTrue(executionThread.get()?.startsWith("disk-cache") == true)
    }
}
