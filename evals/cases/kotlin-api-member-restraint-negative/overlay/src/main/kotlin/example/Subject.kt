package example

class ProfileTitle {
    fun render(user: User): String = format(user.name)

    private fun format(name: String): String = name.trim().replaceFirstChar(Char::uppercase)
}
