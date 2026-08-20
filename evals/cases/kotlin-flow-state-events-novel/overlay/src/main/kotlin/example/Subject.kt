package example

import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow

class ProfileModel {
    private val mutableState = MutableStateFlow("loading")
    val state: StateFlow<String> = mutableState.asStateFlow()

    private val mutableNavigation = MutableSharedFlow<String>()
    val navigation: SharedFlow<String> = mutableNavigation.asSharedFlow()
}
