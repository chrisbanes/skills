package example

data class User(val id: String, val name: String)

interface UserApi {
    suspend fun fetchUser(): User
}
