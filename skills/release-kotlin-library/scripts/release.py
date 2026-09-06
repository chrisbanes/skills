#!/usr/bin/env python3
"""Prepare and verify a bounded Kotlin library release.

Adapted from Haze's ``scripts/release.py`` (Apache-2.0), commit
3eb4b565d8140ff7e3b7404864267967afc830e3. This helper keeps
the useful Gradle property, API snapshot, and changelog conventions, but
deliberately separates reversible preparation from publication.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence


VERSION = re.compile(r"^[0-9]+(?:\.[0-9]+)+(?:-[0-9A-Za-z][0-9A-Za-z.-]*)?$")
ENV_KEY = re.compile(r"(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)[ \t]*=[ \t]*(.*)$")
CommandRunner = Callable[..., str]


class RecoveryRequired(RuntimeError):
    """A remote or publication state needs an explicit human recovery decision."""


@dataclass(frozen=True)
class PrepareResult:
    release_version: str
    release_sha: str
    tag: str


@dataclass(frozen=True)
class PublishResult:
    completed: bool
    output: str


def require(value: Any, message: str) -> Any:
    if not value:
        raise ValueError(message)
    return value


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


def validate_release_version(config: Mapping[str, Any]) -> str:
    release = require(config.get("release_version"), "release_version is required")
    if not isinstance(release, str) or not VERSION.fullmatch(release) or release.endswith("-SNAPSHOT"):
        raise ValueError("release_version must be an explicit non-SNAPSHOT Maven version")
    return release


def validate_versions(config: Mapping[str, Any]) -> tuple[str, str]:
    release = validate_release_version(config)
    next_version = require(config.get("next_version"), "next_version is required")
    if not isinstance(next_version, str) or not VERSION.fullmatch(next_version) or not next_version.endswith("-SNAPSHOT"):
        raise ValueError("next_version must be an explicit Maven -SNAPSHOT version")
    return release, next_version


def root_path(root: Path, configured_path: str, *, must_exist: bool = False) -> Path:
    if not isinstance(configured_path, str) or not configured_path or Path(configured_path).is_absolute():
        raise ValueError("configured paths must be non-empty paths relative to the repository root")
    candidate = (root / configured_path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"configured path escapes repository root: {configured_path}") from error
    if must_exist and not candidate.exists():
        raise ValueError(f"required path does not exist: {configured_path}")
    return candidate


def get_property(key: str, path: Path) -> str:
    require_string(key, "version_key")
    values = [line.split("=", 1)[1].strip() for line in path.read_text(encoding="utf-8").splitlines()
              if line.startswith(f"{key}=")]
    if len(values) != 1:
        raise ValueError(f"expected exactly one {key} property in {path}")
    return values[0]


def updated_property(key: str, value: str, path: Path) -> str:
    require_string(key, "version_key")
    content = path.read_bytes().decode("utf-8")
    replacement, count = re.subn(
        rf"^{re.escape(key)}=[^\r\n]*", f"{key}={value}", content, flags=re.MULTILINE
    )
    if count != 1:
        raise ValueError(f"expected exactly one {key} property in {path}")
    return replacement


def find_published_api_files(root: Path) -> list[Path]:
    """Return Haze-style API files belonging to modules with POM_ARTIFACT_ID."""
    result = []
    for api_file in root.rglob("api/api.txt"):
        try:
            api_file.resolve().relative_to(root.resolve())
        except ValueError as error:
            raise ValueError(f"API file escapes repository root: {api_file}") from error
        properties = api_file.parent.parent / "gradle.properties"
        if properties.exists() and re.search(
            r"^POM_ARTIFACT_ID=", properties.read_text(encoding="utf-8"), re.MULTILINE
        ):
            result.append(api_file)
    return sorted(result)


def updated_changelog(content: str, changelog: Mapping[str, Any], release: str, date: str) -> str:
    unreleased = require(changelog.get("unreleased_heading"), "changelog.unreleased_heading is required")
    heading_template = require(changelog.get("release_heading"), "changelog.release_heading is required")
    if not isinstance(unreleased, str) or not isinstance(heading_template, str):
        raise ValueError("changelog headings must be strings")
    matches = list(re.finditer(rf"^{re.escape(unreleased)}[ \t]*(?=\r?$)", content, re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f"changelog must contain exactly one {unreleased!r} section")
    heading = heading_template.replace("{version}", release).replace("{date}", date)
    if re.search(r"\{[A-Za-z_][A-Za-z0-9_]*\}", heading):
        raise ValueError("changelog.release_heading only supports {version} and {date}")
    if re.search(rf"^{re.escape(heading)}[ \t]*\r?$", content, re.MULTILINE):
        raise ValueError(f"changelog already contains release heading {release}")
    match = matches[0]
    after = content[match.end():]
    newline = "\r\n" if after.startswith("\r\n") else "\n"
    if not after.startswith(newline):
        raise ValueError("changelog Unreleased heading must occupy a complete line")
    return content[:match.end()] + newline + newline + heading + after


def parse_dotenv(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, original in enumerate(text.splitlines(), start=1):
        line = original.strip()
        if not line or line.startswith("#"):
            continue
        match = ENV_KEY.fullmatch(line)
        if not match:
            raise ValueError(f"unsupported .env syntax on line {number}")
        key, value = match.groups()
        if value.startswith(("'", '"')):
            quote = value[0]
            if len(value) < 2 or not value.endswith(quote):
                raise ValueError(f"unterminated quoted value on line {number}")
            value = value[1:-1]
        elif any(character.isspace() for character in value) or value.startswith("#"):
            raise ValueError(f"unsupported .env syntax on line {number}")
        if "$(" in value or "`" in value or "${" in value:
            raise ValueError(f"unsupported .env syntax on line {number}")
        values[key] = value
    return values


def load_release_env(env_file: Path, process_env: Mapping[str, str] | None = None) -> dict[str, str]:
    """Parse an optional dotenv file as data; process environment wins."""
    file_values = parse_dotenv(env_file.read_text(encoding="utf-8")) if env_file.exists() else {}
    ambient = dict(os.environ if process_env is None else process_env)
    # Preserve a normal child process environment (notably PATH), while giving
    # explicitly supplied process values precedence over ~/.env.
    return file_values | ambient


def subprocess_command(argv: Sequence[str], *, cwd: Path, env: Mapping[str, str] | None = None) -> str:
    result = subprocess.run(
        list(argv), cwd=cwd, env=None if env is None else dict(env), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if result.returncode:
        raise RuntimeError("command failed")
    return result.stdout


def run_git(root: Path, args: Sequence[str], *, allow_failure: bool = False) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode and not allow_failure:
        raise ValueError("git command failed")
    return result.stdout.strip()


def git_status(root: Path) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise ValueError("git status failed")
    return result.stdout.rstrip("\n")


def command_argv(template: Any, config: Mapping[str, Any]) -> list[str]:
    if not isinstance(template, list) or not template or not all(isinstance(item, str) and item for item in template):
        raise ValueError("commands must be non-empty JSON arrays of strings")
    release = validate_release_version(config)
    values = {"release_version": release, "tag": config.get("tag", release)}
    if any("{next_version}" in item for item in template):
        values["next_version"] = validate_versions(config)[1]
    try:
        return [item.format(**values) for item in template]
    except (KeyError, ValueError) as error:
        raise ValueError("command arguments only support {release_version}, {next_version}, and {tag}") from error


def readback_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
    publication = require(config.get("publication"), "publication configuration is required")
    if not isinstance(publication, Mapping):
        raise ValueError("publication must be an object")
    command_argv(publication.get("artifact_check"), config)
    credentials = publication.get("required_credentials", [])
    if not isinstance(credentials, list) or not all(
        isinstance(key, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
        for key in credentials
    ):
        raise ValueError("publication.required_credentials must be environment variable names")
    return publication


def publication_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_versions(config)
    publication = readback_config(config)
    if not isinstance(publication.get("mode"), str) or publication["mode"] not in {"local", "tag-ci"}:
        raise ValueError("publication.mode must be local or tag-ci")
    if publication["mode"] == "local":
        command_argv(publication.get("command"), config)
    else:
        command_argv(publication.get("ci_check"), config)
    return publication


def config_digest(config: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def release_paths(root: Path, config: Mapping[str, Any]) -> tuple[Path, Path | None, list[Path]]:
    version_file = root_path(root, require(config.get("version_file"), "version_file is required"), must_exist=True)
    changelog_config = config.get("changelog")
    changelog_path = None
    if changelog_config is not None:
        if not isinstance(changelog_config, Mapping):
            raise ValueError("changelog must be an object or null")
        changelog_path = root_path(root, require(changelog_config.get("path"), "changelog.path is required"))
    api_mode = config.get("api_snapshots", "haze-published")
    if not isinstance(api_mode, str) or api_mode not in {"haze-published", "disabled"}:
        raise ValueError("api_snapshots must be haze-published or disabled")
    api_files = find_published_api_files(root) if api_mode == "haze-published" else []
    return version_file, changelog_path, api_files


def common_preflight(root: Path, config: Mapping[str, Any], *, require_prepared: bool) -> None:
    release, _ = validate_versions(config)
    tag = config.get("tag", release)
    if not isinstance(tag, str) or not tag:
        raise ValueError("tag must be a non-empty string")
    branch = require_string(config.get("branch"), "branch")
    remote = require(config.get("remote"), "remote is required")
    if not isinstance(remote, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", remote):
        raise ValueError("remote must be a simple Git remote name")
    run_git(root, ["check-ref-format", "--branch", branch])
    run_git(root, ["check-ref-format", f"refs/tags/{tag}"])
    if git_status(root):
        raise ValueError("repository and index must be clean before release work")
    if run_git(root, ["branch", "--show-current"]) != branch:
        raise ValueError(f"release must run on configured branch {branch}")
    run_git(root, ["remote", "get-url", remote])
    version_file, _changelog, _api_files = release_paths(root, config)
    version = get_property(require(config.get("version_key"), "version_key is required"), version_file)
    local_tag = run_git(root, ["rev-parse", "--verify", f"refs/tags/{tag}"], allow_failure=True)
    if require_prepared:
        if local_tag != run_git(root, ["rev-parse", "HEAD"]):
            raise RecoveryRequired("prepared release tag must point at HEAD")
        if version != release:
            raise RecoveryRequired("prepared release commit does not contain the release version")
    else:
        if local_tag:
            raise ValueError(f"release tag {tag} already exists locally")
        if not version.endswith("-SNAPSHOT"):
            raise ValueError("current version property must be a -SNAPSHOT version")
    remote_tag = run_git(root, ["ls-remote", "--tags", remote, f"refs/tags/{tag}"])
    if remote_tag:
        raise RecoveryRequired(f"release tag {tag} already exists remotely; inspect before retrying")
    remote_branch = run_git(root, ["ls-remote", remote, f"refs/heads/{branch}"])
    if not remote_branch:
        raise ValueError("configured remote branch is absent; resolve the release destination first")
    remote_sha = remote_branch.split()[0]
    try:
        run_git(root, ["merge-base", "--is-ancestor", remote_sha, "HEAD"])
    except ValueError as error:
        raise ValueError("remote branch is not a known ancestor; refresh and reconcile before release") from error
    if require_prepared and remote_sha == run_git(root, ["rev-parse", "HEAD"]):
        raise RecoveryRequired("prepared release commit already exists on remote branch; inspect before retrying")


def require_config_binding(root: Path, config: Mapping[str, Any]) -> None:
    expected = f"Release-Config-SHA256: {config_digest(config)}"
    message = run_git(root, ["log", "-1", "--format=%B"])
    if expected not in message.splitlines():
        raise RecoveryRequired("current prepared release commit was made with different release configuration")


def require_prepared_intact(root: Path, config: Mapping[str, Any], prepared_sha: str) -> None:
    release, _ = validate_versions(config)
    tag = config.get("tag", release)
    if git_status(root) or run_git(root, ["rev-parse", "HEAD"]) != prepared_sha:
        raise RecoveryRequired("prepared release state changed; inspect before publishing")
    if run_git(root, ["rev-parse", "--verify", f"refs/tags/{tag}"], allow_failure=True) != prepared_sha:
        raise RecoveryRequired("prepared release tag changed; inspect before publishing")
    require_config_binding(root, config)


def non_publication_env(config: Mapping[str, Any], process_env: Mapping[str, str] | None = None) -> dict[str, str]:
    environment = dict(os.environ if process_env is None else process_env)
    for key in readback_config(config).get("required_credentials", []):
        environment.pop(key, None)
    return environment


def run_checks(root: Path, config: Mapping[str, Any], command_runner: CommandRunner,
               process_env: Mapping[str, str] | None = None) -> None:
    checks = config.get("checks", [])
    if not isinstance(checks, list):
        raise ValueError("checks must be a list of command arrays")
    for check in checks:
        command_runner(command_argv(check, config), cwd=root, env=non_publication_env(config, process_env))


def expected_worktree_changes(root: Path, files: Mapping[Path, str]) -> None:
    expected = {str(path.relative_to(root)) for path in files}
    for entry in git_status(root).splitlines():
        if len(entry) < 4 or entry[3:] not in expected or entry[:2] not in {" M", "??"}:
            raise ValueError(f"release check changed or staged files outside the prepared release scope: {entry!r}")
    for path, expected_content in files.items():
        if path.read_bytes().decode("utf-8") != expected_content:
            raise ValueError("release check modified a prepared release file")


def prepare(root: Path, config: Mapping[str, Any], *, command_runner: CommandRunner = subprocess_command) -> PrepareResult:
    root = root.resolve()
    publication_config(config)
    checks = config.get("checks", [])
    if not isinstance(checks, list):
        raise ValueError("checks must be a list of command arrays")
    for check in checks:
        command_argv(check, config)
    common_preflight(root, config, require_prepared=False)
    release, _next = validate_versions(config)
    version_file, changelog_path, api_files = release_paths(root, config)
    version_key = require(config.get("version_key"), "version_key is required")
    version_content = updated_property(version_key, release, version_file)
    date = config.get("release_date", dt.date.today().isoformat())
    if not isinstance(date, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date):
        raise ValueError("release_date must use YYYY-MM-DD")
    try:
        dt.date.fromisoformat(date)
    except ValueError as error:
        raise ValueError("release_date must use YYYY-MM-DD") from error
    changelog_content = None
    if changelog_path is not None and changelog_path.exists():
        changelog_content = updated_changelog(changelog_path.read_bytes().decode("utf-8"), config["changelog"], release, date)
    snapshots = [(api_file.parent / f"{release}.txt", api_file.read_bytes().decode("utf-8")) for api_file in api_files]
    for snapshot, _content in snapshots:
        if snapshot.exists():
            raise ValueError(f"API snapshot already exists: {snapshot.relative_to(root)}")
    initial_sha = run_git(root, ["rev-parse", "HEAD"])
    originals = {version_file: version_file.read_bytes()}
    if changelog_content is not None:
        originals[changelog_path] = changelog_path.read_bytes()
    originals.update({path: None for path, _ in snapshots})
    planned_files = {version_file: version_content}
    if changelog_content is not None:
        planned_files[changelog_path] = changelog_content
    planned_files.update(snapshots)
    for path, content in planned_files.items():
        path.write_bytes(content.encode("utf-8"))
    # Bind validation evidence to the exact prepared release content. Checks
    # never receive release credentials.
    try:
        run_checks(root, config, command_runner)
        if run_git(root, ["rev-parse", "HEAD"]) != initial_sha:
            raise ValueError("release check changed HEAD")
        expected_worktree_changes(root, planned_files)
    except Exception as error:
        # Restore only unchanged, unstaged files still owned by this attempt.
        # Never reset the index or discard edits made by a check or another actor.
        staged = set(run_git(root, ["diff", "--cached", "--name-only", "-z"]).split("\0"))
        if run_git(root, ["rev-parse", "HEAD"]) == initial_sha:
            for path, content in planned_files.items():
                if (str(path.relative_to(root)) not in staged and path.is_file()
                        and path.read_bytes().decode("utf-8") == content):
                    if originals[path] is None:
                        path.unlink()
                    else:
                        path.write_bytes(originals[path])
        message = ("preparation check failed; unchanged helper-owned files restored; "
                   "inspect remaining worktree/index changes before retrying")
        if isinstance(error, ValueError):
            raise ValueError(message) from None
        raise RuntimeError(message) from None
    relative = [str(path.relative_to(root)) for path in planned_files]
    run_git(root, ["add", "--", *relative])
    run_git(
        root,
        [
            "commit", "-m", f"Prepare for release {release}\n\n"
            f"Release-Config-SHA256: {config_digest(config)}",
        ],
    )
    tag = config.get("tag", release)
    run_git(root, ["tag", tag])
    return PrepareResult(release_version=release, release_sha=run_git(root, ["rev-parse", "HEAD"]), tag=tag)


def artifact_state(root: Path, config: Mapping[str, Any], command_runner: CommandRunner,
                   process_env: Mapping[str, str] | None = None) -> str:
    output = command_runner(command_argv(readback_config(config)["artifact_check"], config), cwd=root, env=non_publication_env(config, process_env))
    try:
        state = json.loads(output)["state"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise RecoveryRequired("artifact verifier returned an unreadable state") from error
    if state not in {"absent", "published", "unknown"}:
        raise RecoveryRequired("artifact verifier returned an unsupported state")
    return state


def credential_environment(config: Mapping[str, Any], process_env: Mapping[str, str]) -> dict[str, str]:
    publication = publication_config(config)
    configured = config.get("env_file", "~/.env")
    env_file = Path(configured).expanduser() if isinstance(configured, str) else None
    if env_file is None:
        raise ValueError("env_file must be a path string")
    loaded = load_release_env(env_file, process_env)
    credentials = publication.get("required_credentials", [])
    missing = [key for key in credentials if not loaded.get(key) and not process_env.get(key)]
    if missing:
        raise ValueError("required release credentials are unavailable: " + ", ".join(missing))
    child = dict(process_env)
    child.update({key: loaded[key] for key in credentials})
    return child


def verify_remote_git(root: Path, config: Mapping[str, Any]) -> None:
    release, _ = validate_versions(config)
    tag = config.get("tag", release)
    remote = config["remote"]
    branch = config["branch"]
    sha = run_git(root, ["rev-parse", "HEAD"])
    remote_branch = run_git(root, ["ls-remote", remote, f"refs/heads/{branch}"])
    remote_tag = run_git(root, ["ls-remote", remote, f"refs/tags/{tag}"])
    if not remote_branch.startswith(sha) or not remote_tag.startswith(sha):
        raise RecoveryRequired("remote branch or tag does not verify the prepared release commit")


def publish(root: Path, config: Mapping[str, Any], *, command_runner: CommandRunner = subprocess_command,
            process_env: Mapping[str, str] | None = None) -> PublishResult:
    root = root.resolve()
    publication = publication_config(config)
    common_preflight(root, config, require_prepared=True)
    require_config_binding(root, config)
    prepared_sha = run_git(root, ["rev-parse", "HEAD"])
    try:
        run_checks(root, config, command_runner, process_env)
    except Exception as error:
        raise RecoveryRequired("prepared release validation failed; inspect before publishing") from error
    require_prepared_intact(root, config, prepared_sha)
    try:
        state = artifact_state(root, config, command_runner, process_env)
    except Exception as error:
        raise RecoveryRequired("artifact inspection failed; inspect recovery state before publishing") from error
    if state != "absent":
        raise RecoveryRequired(f"artifact state is {state}; inspect recovery state before retrying publication")
    require_prepared_intact(root, config, prepared_sha)
    if publication["mode"] == "local":
        environment = credential_environment(config, dict(os.environ if process_env is None else process_env))
    try:
        if publication["mode"] == "local":
            command_runner(command_argv(publication["command"], config), cwd=root, env=environment)
        else:
            run_git(root, ["push", config["remote"], f"HEAD:refs/heads/{config['branch']}"])
            run_git(root, ["push", config["remote"], config.get("tag", config["release_version"])])
            ci = command_runner(command_argv(publication["ci_check"], config), cwd=root, env=non_publication_env(config, process_env))
            try:
                ci_state = json.loads(ci)["state"]
            except (json.JSONDecodeError, KeyError, TypeError) as error:
                raise RecoveryRequired("CI verifier returned an unreadable state") from error
            if ci_state != "passed":
                raise RecoveryRequired("CI verification did not pass; inspect before retrying")
    except RecoveryRequired:
        raise
    except Exception as error:
        raise RecoveryRequired("publication command failed; inspect remote and artifact state before retrying") from error
    try:
        final_state = artifact_state(root, config, command_runner, process_env)
    except Exception as error:
        raise RecoveryRequired("artifact verification failed; inspect recovery state before retrying") from error
    if final_state != "published":
        raise RecoveryRequired("artifact did not verify as published; do not retry automatically")
    require_prepared_intact(root, config, prepared_sha)
    if publication["mode"] == "local":
        try:
            run_git(root, ["push", config["remote"], f"HEAD:refs/heads/{config['branch']}"])
            run_git(root, ["push", config["remote"], config.get("tag", config["release_version"])])
        except Exception as error:
            raise RecoveryRequired("artifact published but Git push failed; inspect before retrying") from error
    verify_remote_git(root, config)
    version_file, _changelog, _api_files = release_paths(root, config)
    _release, next_version = validate_versions(config)
    version_file.write_bytes(updated_property(config["version_key"], next_version, version_file).encode("utf-8"))
    try:
        run_git(root, ["add", "--", str(version_file.relative_to(root))])
        run_git(root, ["commit", "-m", "Prepare next development version"])
        run_git(root, ["push", config["remote"], f"HEAD:refs/heads/{config['branch']}"])
        next_sha = run_git(root, ["rev-parse", "HEAD"])
        remote_branch = run_git(root, ["ls-remote", config["remote"], f"refs/heads/{config['branch']}"])
        if not remote_branch.startswith(next_sha):
            raise RecoveryRequired("next development branch did not verify after push")
    except Exception as error:
        raise RecoveryRequired("release verified but next development version could not be completed; inspect before retrying") from error
    return PublishResult(completed=True, output="publication and verification completed")


def recover(root: Path, config: Mapping[str, Any], *, command_runner: CommandRunner = subprocess_command) -> dict[str, str]:
    """Read live recovery evidence without publishing, pushing, or changing files."""
    root = root.resolve()
    readback_config(config)
    release = validate_release_version(config)
    tag = require_string(config.get("tag", release), "tag")
    remote = require_string(config.get("remote"), "remote")
    branch = require_string(config.get("branch"), "branch")
    def remote_state(args: Sequence[str]) -> str:
        try:
            return run_git(root, args) or "absent"
        except ValueError:
            return "unknown"

    try:
        artifact = artifact_state(root, config, command_runner)
    except Exception:
        artifact = "unknown"
    return {
        "artifact": artifact,
        "local_tag": run_git(root, ["rev-parse", "--verify", f"refs/tags/{tag}"], allow_failure=True) or "absent",
        "remote_tag": remote_state(["ls-remote", "--tags", remote, f"refs/tags/{tag}"]),
        "remote_branch": remote_state(["ls-remote", remote, f"refs/heads/{branch}"]),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, required=True, help="Repository-specific release JSON")
    parser.add_argument("command", choices=("preflight", "prepare", "publish", "recover"))
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("release config must be a JSON object")
        if args.command == "preflight":
            publication_config(config)
            common_preflight(args.root.resolve(), config, require_prepared=False)
            run_checks(args.root.resolve(), config, subprocess_command)
        elif args.command == "prepare":
            print(json.dumps(prepare(args.root, config).__dict__, sort_keys=True))
        elif args.command == "publish":
            print(json.dumps(publish(args.root, config).__dict__, sort_keys=True))
        else:
            print(json.dumps(recover(args.root, config), sort_keys=True))
    except (ValueError, RecoveryRequired, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
