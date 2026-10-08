import importlib.util
import contextlib
import io
import json
import os
import pathlib
import subprocess
import tempfile
import textwrap
import unittest
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
RELEASE_SCRIPT = ROOT / "scripts" / "release.py"


def load_release_module():
    spec = importlib.util.spec_from_file_location("release", RELEASE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseScriptTest(unittest.TestCase):
    def setUp(self):
        self.release = load_release_module()

    def test_validate_version_accepts_non_zero_padded_calver(self):
        self.assertEqual(self.release.validate_version("2026.6.17"), "2026.6.17")

    def test_validate_version_accepts_daily_release_number(self):
        expected_versions = {
            "2026.6.17.1": "2026.6.17.01",
            "2026.6.17.01": "2026.6.17.01",
            "2026.6.17.99": "2026.6.17.99",
        }
        for version, expected in expected_versions.items():
            with self.subTest(version=version):
                self.assertEqual(self.release.validate_version(version), expected)

    def test_resolve_version_canonicalizes_daily_release_number(self):
        self.assertEqual(self.release.resolve_version("2026.6.17.1"), "2026.6.17.01")

    def test_automatic_version_uses_next_daily_number(self):
        cases = [
            ([], "2026.6.17"),
            (["2026.6.17"], "2026.6.17.01"),
            (["2026.6.17", "2026.6.17.01"], "2026.6.17.02"),
            (["2026.6.17.1", "2026.6.17.09", "2026.6.17.09"], "2026.6.17.10"),
            (["2026.6.16.99", "2026.6.18", "unrelated", "2026.6.17.001"], "2026.6.17"),
            (["2026.6.17.98"], "2026.6.17.99"),
            (["2026.06.17"], "2026.6.17.01"),
            (["2026.06.17.01", "2026.6.17.1"], "2026.6.17.02"),
            (["2026.06.07.9"], "2026.6.17"),
            (["2026.006.17", "2026.6.017", "2026.06.17.001"], "2026.6.17"),
        ]
        with patch.object(self.release, "default_version", return_value="2026.6.17"):
            for versions, expected in cases:
                with self.subTest(versions=versions):
                    self.assertEqual(self.release.resolve_version("", versions), expected)

    def test_automatic_version_fails_when_daily_numbers_exhausted(self):
        with patch.object(self.release, "default_version", return_value="2026.6.17"):
            for version in ("2026.6.17.99", "2026.06.17.99"):
                with self.subTest(version=version), self.assertRaisesRegex(ValueError, "exhausted"):
                    self.release.resolve_version("", [version])

    def test_cli_reads_existing_versions_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            inventory = pathlib.Path(tmp) / "release-versions.txt"
            inventory.write_text("2026.06.17\n2026.6.17.01\n2026.6.17.09\n", encoding="utf-8")
            output = io.StringIO()
            with patch.object(self.release, "default_version", return_value="2026.6.17"):
                with contextlib.redirect_stdout(output):
                    result = self.release.main(["resolve-version", "--existing-versions", str(inventory)])
            self.assertEqual(result, 0)
            self.assertEqual(output.getvalue(), "2026.6.17.10\n")

    def test_explicit_version_remains_an_override(self):
        self.assertEqual(
            self.release.resolve_version("2026.6.17.1", ["2026.6.17.99"]),
            "2026.6.17.01",
        )

    def test_workflow_hands_inventory_to_cli_and_skips_listing_for_override(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        step = workflow.split("      - name: Resolve version\n", 1)[1].split("\n      - name:", 1)[0]
        script = textwrap.dedent(step.split("        run: |\n", 1)[1])
        today = self.release.default_version()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            git = bin_dir / "git"
            git.write_text('#!/bin/sh\nif [ "$1" = tag ]; then echo "$TEST_TODAY"; fi\n', encoding="utf-8")
            gh = bin_dir / "gh"
            gh.write_text('#!/bin/sh\nif [ -n "$INPUT_VERSION" ]; then exit 1; fi\necho "$TEST_TODAY.09"\n', encoding="utf-8")
            git.chmod(0o755)
            gh.chmod(0o755)
            for input_version, expected in (("", f"{today}.10"), ("2026.6.17.1", "2026.6.17.01")):
                with self.subTest(input_version=input_version):
                    output = root / "output"
                    output.write_text("", encoding="utf-8")
                    result = subprocess.run(
                        ["bash", "-c", script], cwd=ROOT, capture_output=True, text=True,
                        env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                             "TEST_TODAY": today, "INPUT_VERSION": input_version,
                             "RUNNER_TEMP": tmp, "GITHUB_OUTPUT": str(output),
                             "GITHUB_REPOSITORY": "chrisbanes/skills"},
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(output.read_text(encoding="utf-8"), f"version={expected}\n")

    def test_validate_version_rejects_out_of_range_daily_release_number(self):
        for version in ("2026.6.17.0", "2026.6.17.00", "2026.6.17.001", "2026.6.17.100"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.release.validate_version(version)

    def test_validate_version_rejects_zero_padded_calver(self):
        with self.assertRaises(ValueError):
            self.release.validate_version("2026.06.17")

    def test_repository_manifests_are_valid(self):
        version = self.read_json(ROOT / "plugin.json")["version"]
        self.release.validate_manifests(ROOT, version)

    def test_update_and_validate_manifests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / ".claude-plugin").mkdir()
            (root / ".codex-plugin").mkdir()
            (root / ".agents" / "plugins").mkdir(parents=True)

            self.write_json(
                root / "plugin.json",
                {
                    "$schema": self.release.AGENT_PLUGINS_SCHEMA,
                    "name": "chrisbanes-skills",
                    "version": "2026.6.16",
                },
            )
            self.write_json(
                root / ".claude-plugin" / "plugin.json",
                {"name": "chrisbanes-skills", "version": "2026.6.16"},
            )
            self.write_json(
                root / ".codex-plugin" / "plugin.json",
                {"name": "chrisbanes-skills", "version": "2026.6.16", "skills": "./skills/"},
            )
            self.write_json(
                root / "package.json",
                {
                    "name": "chrisbanes-skills",
                    "version": "2026.6.16",
                    "main": ".opencode/plugins/chrisbanes-skills.js",
                },
            )
            self.write_json(
                root / ".claude-plugin" / "marketplace.json",
                {"name": "chrisbanes-skills"},
            )
            self.write_json(
                root / ".agents" / "plugins" / "marketplace.json",
                {"name": "chrisbanes-skills"},
            )

            self.release.update_manifests(root, "2026.6.17.1")
            self.release.validate_manifests(root, "2026.6.17.1")

            portable = self.read_json(root / "plugin.json")
            claude = self.read_json(root / ".claude-plugin" / "plugin.json")
            codex = self.read_json(root / ".codex-plugin" / "plugin.json")
            package = self.read_json(root / "package.json")
            self.assertEqual(portable["version"], "2026.6.17.01")
            self.assertEqual(claude["version"], "2026.6.17.01")
            self.assertEqual(codex["version"], "2026.6.17.01")
            self.assertEqual(package["version"], "2026.6.17.01")

    def test_validate_manifests_rejects_opencode_package_name_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.write_valid_manifests(root)
            package_path = root / "package.json"
            package = self.read_json(package_path)
            package["name"] = "wrong-name"
            self.write_json(package_path, package)

            with self.assertRaisesRegex(ValueError, "OpenCode package name"):
                self.release.validate_manifests(root, "2026.6.17")

    def test_validate_manifests_rejects_agent_plugins_schema_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.write_valid_manifests(root)
            portable_path = root / "plugin.json"
            portable = self.read_json(portable_path)
            portable["$schema"] = "https://example.com/plugin.schema.json"
            self.write_json(portable_path, portable)

            with self.assertRaisesRegex(ValueError, "Agent Plugins schema"):
                self.release.validate_manifests(root, "2026.6.17")

    def test_validate_manifests_rejects_unknown_agent_plugins_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.write_valid_manifests(root)
            portable_path = root / "plugin.json"
            portable = self.read_json(portable_path)
            portable["skills"] = "./skills/"
            self.write_json(portable_path, portable)

            with self.assertRaisesRegex(ValueError, "unknown fields"):
                self.release.validate_manifests(root, "2026.6.17")

    def test_validate_manifests_rejects_opencode_package_version_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.write_valid_manifests(root)
            package_path = root / "package.json"
            package = self.read_json(package_path)
            package["version"] = "2026.6.16"
            self.write_json(package_path, package)

            with self.assertRaisesRegex(ValueError, "OpenCode package version"):
                self.release.validate_manifests(root, "2026.6.17")

    def test_validate_manifests_rejects_opencode_package_main_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.write_valid_manifests(root)
            package_path = root / "package.json"
            package = self.read_json(package_path)
            package["main"] = "index.js"
            self.write_json(package_path, package)

            with self.assertRaisesRegex(ValueError, "OpenCode package main"):
                self.release.validate_manifests(root, "2026.6.17")

    def write_valid_manifests(self, root, version="2026.6.17"):
        (root / ".claude-plugin").mkdir()
        (root / ".codex-plugin").mkdir()
        (root / ".agents" / "plugins").mkdir(parents=True)

        self.write_json(
            root / "plugin.json",
            {
                "$schema": self.release.AGENT_PLUGINS_SCHEMA,
                "name": "chrisbanes-skills",
                "version": version,
            },
        )
        self.write_json(
            root / ".claude-plugin" / "plugin.json",
            {"name": "chrisbanes-skills", "version": version},
        )
        self.write_json(
            root / ".codex-plugin" / "plugin.json",
            {"name": "chrisbanes-skills", "version": version, "skills": "./skills/"},
        )
        self.write_json(
            root / "package.json",
            {
                "name": "chrisbanes-skills",
                "version": version,
                "main": ".opencode/plugins/chrisbanes-skills.js",
            },
        )
        self.write_json(
            root / ".claude-plugin" / "marketplace.json",
            {"name": "chrisbanes-skills"},
        )
        self.write_json(
            root / ".agents" / "plugins" / "marketplace.json",
            {"name": "chrisbanes-skills"},
        )

    @staticmethod
    def write_json(path, value):
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def read_json(path):
        return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
