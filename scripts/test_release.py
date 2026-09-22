import importlib.util
import json
import pathlib
import tempfile
import unittest


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
