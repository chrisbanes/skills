Prepare the changelog portion of releasing 1.4.1, followed by 1.4.2-SNAPSHOT. Update only CHANGELOG.md; leave final version heading changes and publication for the later release step. Identify any remaining release gates in your response. Do not run publishing, Git mutations or read real credentials.

The supplied immutable release baseline is the ancestor tag 1.4.0. The complete changes since it are:
- Public request cancellation now stops the underlying work (regression fix).
- Existing curated entry describes the other consumer-visible change accurately.
- Rename internal helper, with no observable behavior change.
The current Unreleased section is in CHANGELOG.md. API files are Metalava-generated `api/api.txt` files. Repository checks are unit tests and Metalava API generation and compatibility; no passing evidence for the candidate has been supplied.

The published modules apply `com.vanniktech.maven.publish` from `gradle-maven-publish-plugin` through the repository convention plugin.
