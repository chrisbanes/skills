package example

interface ProfileStore {
    fun load(rawUserId: String): User
}

fun String.loadProfile(store: ProfileStore): User = store.load(this)

fun profileFor(rawUserId: String, store: ProfileStore): User =
    rawUserId.loadProfile(store)
