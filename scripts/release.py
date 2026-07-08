#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import re
import sys


VERSION_PATTERN = re.compile(r"^[0-9]{4}\.([1-9]|1[0-2])\.([1-9]|[12][0-9]|3[01])$")
PLUGIN_NAME = "chrisbanes-skills"
OPENCODE_MAIN = ".opencode/plugins/chrisbanes-skills.js"


def validate_version(version):
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(
            "Version must use SemVer-compatible CalVer YYYY.M.D without "
            f"zero-padded month/day: {version}"
        )
    return version


def default_version():
    today = dt.datetime.now(dt.timezone.utc).date()
    return f"{today.year}.{today.month}.{today.day}"


def resolve_version(input_version):
    if input_version:
        return validate_version(input_version)
    return default_version()


def update_manifests(root, version):
    validate_version(version)
    for path in plugin_manifest_paths(root):
        data = read_json(path)
        data["version"] = version
        write_json(path, data)


def validate_manifests(root, version):
    validate_version(version)

    claude = read_json(root / ".claude-plugin" / "plugin.json")
    codex = read_json(root / ".codex-plugin" / "plugin.json")
    package = read_json(root / "package.json")
    claude_marketplace = read_json(root / ".claude-plugin" / "marketplace.json")
    codex_marketplace = read_json(root / ".agents" / "plugins" / "marketplace.json")

    require(claude.get("name") == PLUGIN_NAME, "Claude plugin name must be chrisbanes-skills")
    require(codex.get("name") == PLUGIN_NAME, "Codex plugin name must be chrisbanes-skills")
    require(package.get("name") == PLUGIN_NAME, "OpenCode package name must be chrisbanes-skills")
    require(claude.get("version") == version, f"Claude plugin version mismatch: {claude.get('version')}")
    require(codex.get("version") == version, f"Codex plugin version mismatch: {codex.get('version')}")
    require(package.get("version") == version, f"OpenCode package version mismatch: {package.get('version')}")
    require(
        claude_marketplace.get("name") == PLUGIN_NAME,
        "Claude marketplace name must be chrisbanes-skills",
    )
    require(
        codex_marketplace.get("name") == PLUGIN_NAME,
        "Codex marketplace name must be chrisbanes-skills",
    )
    require(codex.get("skills") == "./skills/", "Codex plugin skills path must be ./skills/")
    require(package.get("main") == OPENCODE_MAIN, f"OpenCode package main must be {OPENCODE_MAIN}")


def plugin_manifest_paths(root):
    return [
        root / ".claude-plugin" / "plugin.json",
        root / ".codex-plugin" / "plugin.json",
        root / "package.json",
    ]


def read_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Release helpers for chrisbanes-skills.")
    parser.add_argument(
        "--root",
        default=".",
        type=pathlib.Path,
        help="Repository root. Defaults to the current directory.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve-version")
    resolve_parser.add_argument("input_version", nargs="?", default="")

    update_parser = subparsers.add_parser("update-manifests")
    update_parser.add_argument("version")

    validate_parser = subparsers.add_parser("validate-manifests")
    validate_parser.add_argument("version")

    args = parser.parse_args(argv)
    root = args.root.resolve()

    try:
        if args.command == "resolve-version":
            print(resolve_version(args.input_version))
        elif args.command == "update-manifests":
            update_manifests(root, args.version)
        elif args.command == "validate-manifests":
            validate_manifests(root, args.version)
        else:
            parser.error(f"Unknown command: {args.command}")
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
