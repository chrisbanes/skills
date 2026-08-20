package example

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

class UserRepository(
    private val scope: CoroutineScope,
    private val api: UserApi,
) {
    fun refresh() {
        scope.launch { api.fetchUser() }
    }
}
