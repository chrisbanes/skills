package example

class AndroidPermissionRequester(
    private val activityName: String,
) {
    fun requestAndroidPermission(permission: String): Boolean =
        activityName.isNotBlank() && permission.isNotBlank()
}

class SharedProfileScreen(
    private val permissions: AndroidPermissionRequester,
) {
    fun enableCamera(): Boolean = permissions.requestAndroidPermission("CAMERA")
}
