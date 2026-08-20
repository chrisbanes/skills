package example

sealed interface LookupResult {
    data class Found(val user: User) : LookupResult
    data object Missing : LookupResult
    data class Failed(val reason: String) : LookupResult
}

interface LookupStore {
    fun lookup(rawId: String): LookupResult
}

fun String.lookupUser(store: LookupStore): LookupResult = store.lookup(this)

fun label(result: LookupResult): String = when (result) {
    is LookupResult.Found -> result.user.name
    else -> "Unavailable"
}
