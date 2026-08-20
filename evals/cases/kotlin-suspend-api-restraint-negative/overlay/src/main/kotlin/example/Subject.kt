package example

class ExistingRepository(
    private val api: UserApi,
) {
    suspend fun refresh(): User = api.fetchUser()
}
