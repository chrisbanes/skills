package example

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.filterNotNull
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

@OptIn(ExperimentalCoroutinesApi::class)
class CoroutineContractsTest {
    @Test
    fun channelBuffersAcrossCollectorGapAndAppliesBackpressure() = runTest {
        val channel = Channel<String>(capacity = 1)
        val events = channel.receiveAsFlow()
        assertTrue(channel.trySend("first").isSuccess)
        assertTrue(channel.trySend("full").isFailure)
        val waiting = async { channel.send("second") }
        runCurrent()
        assertFalse(waiting.isCompleted)

        assertEquals("first", events.first())
        waiting.await()
        assertEquals("second", events.first())
    }

    @Test
    fun channelCannotRedeliverAfterCollectorIsCancelledBeforeHandling() = runTest {
        val channel = Channel<String>(Channel.BUFFERED)
        val events = channel.receiveAsFlow()
        val received = CompletableDeferred<String>()
        val allowHandling = CompletableDeferred<Unit>()
        val handled = mutableListOf<String>()
        val collector = launch {
            events.collect { event ->
                received.complete(event)
                allowHandling.await()
                handled += event
            }
        }
        channel.send("received")
        assertEquals("received", received.await())
        collector.cancelAndJoin()
        assertTrue(handled.isEmpty())

        channel.send("next")
        assertEquals("next", events.first())
    }

    @Test
    fun pendingStateRedeliversUntilAcknowledgedById() = runTest {
        val item = PendingNavigation(1, "details")
        val pending = MutableStateFlow<PendingNavigation?>(item)
        val pendingNavigation = pending.asStateFlow().filterNotNull()
        fun acknowledge(id: Long) {
            pending.update { current -> current.takeUnless { it?.id == id } }
        }

        val received = CompletableDeferred<PendingNavigation>()
        val allowHandling = CompletableDeferred<Unit>()
        val handled = mutableListOf<PendingNavigation>()
        val collector = launch {
            val request = pendingNavigation.first()
            received.complete(request)
            allowHandling.await()
            handled += request
            acknowledge(request.id)
        }
        assertEquals(item, received.await())
        collector.cancelAndJoin()
        assertTrue(handled.isEmpty())

        launch {
            val request = pendingNavigation.first()
            handled += request
            acknowledge(request.id)
        }.join()
        assertEquals(listOf(item), handled)
        assertNull(pending.value)

        val newer = PendingNavigation(2, "settings")
        pending.value = newer
        acknowledge(item.id)
        assertEquals(newer, pending.value)
    }

    @Test
    fun cancelledDeferredThrowsEvenWhileAwaitingCallerIsActive() = runTest {
        val deferred = CompletableDeferred<String>()
        deferred.cancel(CancellationException("dependency cancelled"))

        val failure = assertFailsWith<CancellationException> {
            recoverLoad {
                try {
                    deferred.await()
                } catch (error: CancellationException) {
                    currentCoroutineContext().ensureActive()
                    throw error
                }
            }
        }
        assertEquals("dependency cancelled", failure.message)
        currentCoroutineContext().ensureActive()
    }

    @Test
    fun broadRecoveryStillHandlesOrdinaryFailure() = runTest {
        assertEquals("fallback", recoverLoad { error("dependency failed") })
        assertEquals("success", recoverLoad { "success" })
    }

    @Test
    fun owningBoundaryTranslatesItsTimeoutAndDistinguishesNullableSuccess() = runTest {
        assertNull(loadWithin(100) { awaitCancellation() })
        assertEquals(Loaded(null), loadWithin(100) { null })
    }

    @Test
    fun timeoutBoundaryPropagatesNestedTimeout() = runTest {
        assertFailsWith<TimeoutCancellationException> {
            loadWithin(200) { withTimeout(100) { awaitCancellation() } }
        }
    }

    @Test
    fun timeoutBoundaryPropagatesCallerCancellation() = runTest {
        val entered = CompletableDeferred<Unit>()
        val propagated = CompletableDeferred<CancellationException>()
        val caller = launch {
            try {
                loadWithin(200) {
                    entered.complete(Unit)
                    awaitCancellation()
                }
            } catch (error: CancellationException) {
                propagated.complete(error)
                throw error
            }
        }
        entered.await()
        caller.cancel(CancellationException("caller cancelled"))
        caller.join()
        assertEquals("caller cancelled", propagated.getCompleted().message)
    }

    @Test
    fun eagerCacheLagsBehindSynchronousProjection() = runTest {
        val userState = MutableStateFlow(User("before"))
        val cachedName = userState
            .map { it.name }
            .stateIn(backgroundScope, SharingStarted.Eagerly, userState.value.name)
        val names = CurrentName(userState)
        runCurrent()

        userState.value = User("after")
        assertEquals("before", cachedName.value)
        assertEquals("after", names.value)

        runCurrent()
        assertEquals("after", cachedName.value)
    }

    private data class PendingNavigation(val id: Long, val destination: String)
    private data class Loaded(val value: String?)
    private data class User(val name: String)

    private class CurrentName(private val userState: MutableStateFlow<User>) {
        val value: String
            get() = userState.value.name
    }

    private suspend fun recoverLoad(load: suspend () -> String): String =
        runCatching { load() }.getOrElse { error ->
            if (error is CancellationException) throw error
            "fallback"
        }

    private suspend fun loadWithin(timeoutMillis: Long, load: suspend () -> String?): Loaded? =
        withTimeoutOrNull(timeoutMillis) { Loaded(load()) }
}
