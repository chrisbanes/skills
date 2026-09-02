package example

import java.nio.file.Files
import java.nio.file.Path
import kotlinx.coroutines.CoroutineDispatcher

class DiskCache(
    private val directory: Path,
    private val dispatcher: CoroutineDispatcher,
    private val deleteExpired: (Path) -> Unit = { Files.deleteIfExists(it) },
) {
    fun evictExpired() {
        Thread {
            deleteExpired(directory.resolve("expired.cache"))
        }.start()
    }
}
