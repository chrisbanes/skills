Read-only: assess whether this Kotlin repository is ready for release from the supplied state. Do not edit files, create a changelog, load credentials, run checks, publish, or contact providers.

There is no CHANGELOG.md. VERSION_NAME is 1.3.0-SNAPSHOT. CI for the current commit passed its documented unit and API checks. The repository publishes via release-tag CI, but no release version or next development version has been selected. No release has been requested. Explain remaining decisions without performing them.

The published modules use only Gradle’s built-in `maven-publish`; `gradle-maven-publish-plugin` is not applied, directly or through a convention plugin.
