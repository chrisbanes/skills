package example

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn

class ProfileNames(scope: CoroutineScope) {
    private val profile = MutableStateFlow(Profile("Initial"))
    val displayName = profile
        .map { it.name.trim() }
        .stateIn(scope, SharingStarted.Eagerly, profile.value.name.trim())

    fun update(name: String) {
        profile.value = Profile(name)
    }

    private data class Profile(val name: String)
}
