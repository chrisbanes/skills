# Bundled release helper

## Supported contract

Use this helper only for libraries using `gradle-maven-publish-plugin`
(`com.vanniktech.maven.publish`). Confirm application in published modules,
including through convention plugins, before configuring it. The helper accepts
explicit commands; it does not detect or enforce this plugin prerequisite itself.

Adapt repository facts into the helper configuration; do not copy a command
from an unrelated project. The helper is based on Haze's `scripts/release.py`
at commit `3eb4b565d8140ff7e3b7404864267967afc830e3`, with preparation moved
before publication. It supports a single shared version property, an optional
Markdown changelog, optional Haze-style Metalava API snapshots, and local or tag-driven
CI publication. Other version stores or release systems need a supported
implementation before this helper can mutate them.

Semantic changelog coverage, version confirmation, authorization and choosing
repository checks remain the agent's responsibility. The helper does not infer
those decisions from a successful command.

## Commands

Resolve the installed skill directory, then use explicit root and config paths:

```sh
python3 <skill-dir>/scripts/release.py --root <repository> --config <config.json> preflight
python3 <skill-dir>/scripts/release.py --root <repository> --config <config.json> prepare
python3 <skill-dir>/scripts/release.py --root <repository> --config <config.json> publish
python3 <skill-dir>/scripts/release.py --root <repository> --config <config.json> recover
```

Run only the command matching the authorized phase. `prepare` creates the
release commit and local tag but does not publish or push. `publish` verifies
the prepared state, publishes and completes Git state. `recover` collects
read-only provider/Git evidence; it does not retry mutations. Recovery requires
only `release_version`, `tag` (or the release-version default), `remote`, `branch`
and `publication.artifact_check`, plus credential names to exclude if applicable.
It does not require `next_version`, a publication mode or a publishing command.
An artifact command that explicitly uses `{next_version}` still requires that
value; use a release-only verifier to inspect an interrupted release. Preparation records a configuration digest in the commit; keep the same config
for publication. Changing it requires inspecting and re-preparing the release.
Check the outcome before advancing. `preflight` is for execution readiness, not a substitute for
a read-only review of supplied evidence.

## Configuration

Keep the JSON configuration outside the working tree. Never put credentials in
it. Use explicit resolved versions, Git destinations, and argument arrays;
commands run without shell interpolation. Command templates accept
`{release_version}`, `{next_version}` and `{tag}`. Discover required credential *names*
from publishing configuration. Keep credentials out of command arguments.

Configure these fields from the repository:

| Field | Meaning |
| --- | --- |
| `release_version`, `next_version` | Confirmed release and next snapshot versions |
| `version_file`, `version_key` | Relative property file and shared version key; Haze uses `gradle.properties` and `VERSION_NAME` |
| `branch`, `remote`, `tag` | Explicit Git destinations and release tag |
| `release_date` | Release date in `YYYY-MM-DD` format |
| `changelog` | Null when absent; otherwise `path`, exact `unreleased_heading`, and `release_heading` template |
| `api_snapshots` | `haze-published` for published-module Metalava API discovery, or `disabled` for repositories without it |
| `checks` | Argument arrays for required validation commands |
| `publication.mode` | `local` or `tag-ci` |
| `publication.command` | Local publishing argument array; omit for tag CI |
| `publication.artifact_check` | Read-only verifier argument array covering every expected artifact/version |
| `publication.ci_check` | Tag-CI verifier argument array bound to the release workflow/commit |
| `publication.required_credentials` | Names required for local publication and stripped from checks/verifiers in either mode; never values |
| `env_file` | Defaults to `~/.env`, loaded only for local publication; use synthetic files in tests |

Haze's changelog heading template is:

```text
## {version} <small>{date}</small> { id="{version}" }
```

Preserve an existing repository style instead of inserting Haze's markup into
plain Markdown. API discovery copies Metalava-generated `api/api.txt` to
`api/<release_version>.txt` only for modules declaring
`POM_ARTIFACT_ID` in their own `gradle.properties`; it does not regenerate API
files or invoke Metalava. Run the repository's configured Metalava generation
and compatibility checks first. Other API dump formats are unsupported by this
snapshot mode; use `disabled` when these Metalava files are not maintained.

For Gradle commands, create the `gradle-run` workflow independently and place
its `run` invocation in each argument array, including a concrete verification
question. Finish that workflow separately after the requested commands finish,
including a blocked run, to remove wrapper-owned sensitive logs. Do not store
raw Gradle output in release evidence or commit a workflow identifier.

## Verification adapters

Use repository-supported commands or small task-local adapters when the
provider does not expose the required result directly. Artifact verification
must report published only when all expected coordinates and versions are
available, absent only when absence is established, and unknown on timeout,
authorization failure or incomplete coverage. Never treat an HTTP error as
proof of absence. CI verification must identify the intended workflow and
release commit, not merely the latest successful run.

Adapters report a JSON object with `state`: artifact states are `published`,
`absent` or `unknown`; successful CI state is `passed`. Supply bounded wait and
polling in the repository-specific verifier when publication is asynchronous.
An unknown result stops completion. Do not replace these checks with commands
that unconditionally print success.

## Credentials and recovery

The environment file is parsed as literal assignments with optional `export`
and single or double quotes. Shell substitution and unsupported syntax are
rejected without printing the line. Explicit process environment values take
precedence. Configured checks and artifact/CI verifiers receive an explicit
environment with the configured release credential names removed, including
credentials already exported by the caller. The configured publishing command retains
those release credentials. Keep credential names configured during recovery so
its artifact verifier is also sanitized. Missing required values block local
publication. Tag-triggered CI uses existing Git authentication and CI-managed
publishing secrets; it does not load or require local dotenv values. Child command output is
sensitive: use only the helper's bounded outcome, never expose raw logs or
request that the user paste secrets.

Preparation requires the configured remote branch to exist and its tip to be a
known ancestor of local HEAD. If not, refresh and reconcile the checkout first.
After a failed check, preparation restores only unchanged, unstaged files owned
by that attempt. It preserves files changed or staged by a check and never resets
the index. Inspect any remaining changes before retrying; do not discard them
with a blanket reset.

If preparation or publication stops, inspect the reported stage and current
Git/artifact state. Preserve the prepared commit and any evidence. Do not rerun
publication to discover whether it worked. A published artifact with an absent
tag requires a verified Git recovery action, not another upload; an unknown
artifact state needs readback first. Manual recovery must remain within the
original authorization and never overwrite existing remote release state.
