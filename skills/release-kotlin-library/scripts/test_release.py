"""Behavior tests for the bounded Kotlin library release helper."""

from __future__ import annotations

import importlib.util
import json
import os
from unittest.mock import patch
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("release.py")


def load_release_module():
    spec = importlib.util.spec_from_file_location("release_kotlin_library", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReleaseHelperTest(unittest.TestCase):
    def setUp(self):
        self.release = load_release_module()
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "library"
        self.root.mkdir()
        self.remote = Path(self.temporary_directory.name) / "remote.git"
        subprocess.run(["git", "init", "--bare", self.remote], check=True, capture_output=True)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "release-test@example.invalid")
        self.git("config", "user.name", "Release Test")
        self.write("gradle.properties", "VERSION_NAME=1.2.0-SNAPSHOT\n")
        self.write(
            "CHANGELOG.md",
            "# Changelog\n\n## Unreleased\n\n- Fixed consumer behavior\n\n"
            "## 1.1.0 <small>2026-01-01</small> { id=\"1.1.0\" }\n\n- Earlier\n",
        )
        self.write("library/api/api.txt", "// API\n")
        self.write("library/gradle.properties", "POM_ARTIFACT_ID=library\n")
        self.write("sample/api/api.txt", "// not published\n")
        self.git("add", ".")
        self.git("commit", "-m", "Initial snapshot")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-u", "origin", "main")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_prepare_creates_release_commit_changelog_and_published_api_snapshot(self):
        result = self.release.prepare(self.root, self.config())

        self.assertEqual(result.release_version, "1.2.0")
        self.assertEqual(self.read("gradle.properties"), "VERSION_NAME=1.2.0\n")
        self.assertTrue((self.root / "library/api/1.2.0.txt").is_file())
        self.assertFalse((self.root / "sample/api/1.2.0.txt").exists())
        self.assertEqual(
            self.read("CHANGELOG.md"),
            "# Changelog\n\n## Unreleased\n\n## 1.2.0 <small>2026-09-06</small> { id=\"1.2.0\" }\n\n"
            "- Fixed consumer behavior\n\n## 1.1.0 <small>2026-01-01</small> { id=\"1.1.0\" }\n\n- Earlier\n",
        )
        self.assertEqual(self.git("log", "-1", "--format=%s"), "Prepare for release 1.2.0")
        self.assertEqual(self.git("tag", "--points-at", "HEAD"), "1.2.0")
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_prepare_skips_a_missing_changelog(self):
        (self.root / "CHANGELOG.md").unlink()
        self.git("add", "CHANGELOG.md")
        self.git("commit", "-m", "No changelog")

        self.release.prepare(self.root, self.config(changelog=None))

        self.assertFalse((self.root / "CHANGELOG.md").exists())

    def test_prepare_rejects_invalid_or_incomplete_inputs_without_writing(self):
        before = self.snapshot()
        for config in (
            self.config(release_version="1.2.0-SNAPSHOT"),
            self.config(release_version="bad version"),
            self.config(next_version="1.3.0"),
        ):
            with self.assertRaises(ValueError):
                self.release.prepare(self.root, config)
            self.assertEqual(self.snapshot(), before)

    def test_prepare_rejects_malformed_changelog_before_writing(self):
        self.write("CHANGELOG.md", "# Changelog\n\n## Future\n")
        self.git("add", "CHANGELOG.md")
        self.git("commit", "-m", "Malformed changelog")
        before = self.snapshot()

        with self.assertRaisesRegex(ValueError, "Unreleased"):
            self.release.prepare(self.root, self.config())

        self.assertEqual(self.snapshot(), before)

    def test_prepare_rejects_untracked_work_before_writing(self):
        self.write("unrelated.txt", "do not stage\n")
        before = self.snapshot()

        with self.assertRaisesRegex(ValueError, "clean"):
            self.release.prepare(self.root, self.config())

        self.assertEqual(self.snapshot(), before)

    def test_prepare_rejects_staged_unrelated_work_without_changing_index(self):
        self.write("unrelated.txt", "preserve this staged content\n")
        self.git("add", "unrelated.txt")
        before = (self.snapshot(), self.git("diff", "--cached"))

        with self.assertRaisesRegex(ValueError, "clean"):
            self.release.prepare(self.root, self.config())

        self.assertEqual(before, (self.snapshot(), self.git("diff", "--cached")))
        self.assertFalse((self.root / "library/api/1.2.0.txt").exists())

    def test_prepare_rejects_existing_snapshot_or_tag_before_writing(self):
        self.write("library/api/1.2.0.txt", "existing\n")
        self.git("add", "library/api/1.2.0.txt")
        self.git("commit", "-m", "Existing snapshot")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.release.prepare(self.root, self.config())
        self.assertEqual(self.snapshot(), before)

        self.git("tag", "1.2.0")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.release.prepare(self.root, self.config())

    def test_dotenv_is_literal_and_process_environment_wins(self):
        env_file = self.root.parent / "release.env"
        canary = "do-not-leak-credential"
        env_file.write_text(
            "export USERNAME=from-file\nTOKEN='" + canary + "'\nEVIL=$(touch pwned)\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.release.load_release_env(env_file, {"USERNAME": "ambient"})
        self.assertFalse((self.root / "pwned").exists())

        env_file.write_text("export USERNAME=from-file\nTOKEN='" + canary + "'\n", encoding="utf-8")
        values = self.release.load_release_env(env_file, {"USERNAME": "ambient"})
        self.assertEqual(values, {"USERNAME": "ambient", "TOKEN": canary})

    def test_publish_requires_absent_then_published_artifact_and_redacts_credentials(self):
        canary = "do-not-leak-credential"
        env_file = self.root.parent / "release.env"
        env_file.write_text("TOKEN='" + canary + "'\n", encoding="utf-8")
        config = self.config(env_file=env_file)
        config["publication"]["required_credentials"] = ["TOKEN"]
        self.release.prepare(self.root, config)
        events = []

        def command(argv, *, cwd, env=None):
            events.append((tuple(argv), None if env is None else env.get("TOKEN")))
            if argv == ["artifact", "1.2.0"]:
                return '{"state":"absent"}' if len(events) == 1 else '{"state":"published"}'
            if argv == ["publish"]:
                self.assertEqual(env["TOKEN"], canary)
                return "published " + canary
            raise AssertionError(argv)

        result = self.release.publish(
            self.root,
            config,
            command_runner=command,
            process_env={},
        )

        self.assertTrue(result.completed)
        self.assertEqual(events, [(("artifact", "1.2.0"), None), (("publish",), canary), (("artifact", "1.2.0"), None)])
        self.assertNotIn(canary, result.output)

    def test_publish_stops_when_artifact_state_is_published_or_unknown(self):
        self.release.prepare(self.root, self.config())
        commands = []
        for state in ("published", "unknown"):
            def command(argv, *, cwd, env=None, state=state):
                commands.append(tuple(argv))
                return json.dumps({"state": state})

            with self.assertRaisesRegex(self.release.RecoveryRequired, state):
                self.release.publish(self.root, self.config(), command_runner=command, process_env={})
        self.assertEqual(commands, [("artifact", "1.2.0"), ("artifact", "1.2.0")])

    def test_publish_refuses_configuration_changed_after_preparation(self):
        config = self.config()
        self.release.prepare(self.root, config)
        config["checks"] = [["changed-check"]]

        with self.assertRaisesRegex(self.release.RecoveryRequired, "different release configuration"):
            self.release.publish(self.root, config, command_runner=lambda *_args, **_kwargs: '{"state":"absent"}', process_env={})

    def test_failed_publication_requires_fresh_unknown_state_to_stop_a_rerun(self):
        config = self.config()
        self.release.prepare(self.root, config)
        calls = []
        state = {"value": "absent"}

        def command(argv, *, cwd, env=None):
            calls.append(tuple(argv))
            if argv == ["artifact", "1.2.0"]:
                return json.dumps({"state": state["value"]})
            if argv == ["publish"]:
                state["value"] = "unknown"
                raise RuntimeError("interrupted publication")
            raise AssertionError(argv)

        with self.assertRaisesRegex(self.release.RecoveryRequired, "publication command failed"):
            self.release.publish(self.root, config, command_runner=command, process_env={})
        with self.assertRaisesRegex(self.release.RecoveryRequired, "artifact state is unknown"):
            self.release.publish(self.root, config, command_runner=command, process_env={})
        self.assertEqual(calls, [("artifact", "1.2.0"), ("publish",), ("artifact", "1.2.0")])

    def test_cli_never_prints_a_credential_from_a_failing_publish_child(self):
        canary = "do-not-leak-from-child"
        env_file = self.root.parent / "release.env"
        env_file.write_text("TOKEN='" + canary + "'\n", encoding="utf-8")
        publisher = self.root.parent / "publish"
        publisher.write_text("#!/bin/sh\nprintf '%s\\n' \"$TOKEN\"\nexit 7\n", encoding="utf-8")
        publisher.chmod(0o755)
        artifact = self.root.parent / "artifact"
        artifact.write_text("#!/bin/sh\nprintf '%s\\n' '{\"state\":\"absent\"}'\n", encoding="utf-8")
        artifact.chmod(0o755)
        config = self.config(env_file=env_file)
        config["publication"].update({
            "command": [str(publisher)],
            "artifact_check": [str(artifact)],
            "required_credentials": ["TOKEN"],
        })
        config_path = self.root.parent / "release.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        prepared = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--config", str(config_path), "prepare"],
            text=True, capture_output=True,
        )
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        published = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--config", str(config_path), "publish"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(published.returncode, 0)
        self.assertNotIn(canary, published.stdout + published.stderr)

    def test_tag_ci_publishes_only_by_pushing_prepared_commit_and_tag_then_verifies(self):
        self.release.prepare(self.root, self.config(publication_mode="tag-ci"))
        events = []

        def command(argv, *, cwd, env=None):
            events.append(tuple(argv))
            if argv == ["artifact", "1.2.0"]:
                return '{"state":"absent"}' if events.count(tuple(argv)) == 1 else '{"state":"published"}'
            if argv == ["ci", "1.2.0"]:
                return '{"state":"passed"}'
            raise AssertionError(argv)

        self.release.publish(self.root, self.config(publication_mode="tag-ci"), command_runner=command, process_env={})

        self.assertEqual(events, [("artifact", "1.2.0"), ("ci", "1.2.0"), ("artifact", "1.2.0")])
        self.assertEqual(self.git("log", "-1", "--format=%s"), "Prepare next development version")
        self.assertEqual(self.read("gradle.properties"), "VERSION_NAME=1.3.0-SNAPSHOT\n")

    def test_artifact_inspection_cannot_change_code_before_publication(self):
        config = self.config()
        self.release.prepare(self.root, config)
        published = []

        def command(argv, *, cwd, env=None):
            if argv == ["artifact", "1.2.0"]:
                self.write("unexpected.txt", "changed during inspection")
                return '{"state":"absent"}'
            published.append(argv)
            return ""

        with self.assertRaises(self.release.RecoveryRequired):
            self.release.publish(self.root, config, command_runner=command, process_env={})
        self.assertEqual([], published)

    def test_invalid_check_contract_fails_before_preparation_writes(self):
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.release.prepare(self.root, self.config(checks=["not-an-argv-array"]))
        self.assertEqual(before, self.snapshot())

    def test_checks_observe_release_version_and_cannot_stage_unrelated_work(self):
        config = self.config(checks=[["check"]])
        initial_sha = self.git("rev-parse", "HEAD")

        def command(argv, *, cwd, env=None):
            self.assertEqual("VERSION_NAME=1.2.0\n", self.read("gradle.properties"))
            self.write("unrelated.txt", "must not commit")
            self.git("add", "unrelated.txt")
            return ""

        with self.assertRaises(ValueError):
            self.release.prepare(self.root, config, command_runner=command)
        self.assertEqual(initial_sha, self.git("rev-parse", "HEAD"))

    def test_remote_inspection_failure_is_unknown_and_blocks_preparation(self):
        self.git("remote", "set-url", "origin", str(self.root.parent / "missing.git"))
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.release.prepare(self.root, self.config())
        self.assertEqual(before, self.snapshot())
        state = self.release.recover(self.root, self.config(), command_runner=lambda *a, **kw: '{"state":"unknown"}')
        self.assertEqual("unknown", state["remote_tag"])
        self.assertEqual("unknown", state["remote_branch"])

    def test_missing_credentials_prevent_publication(self):
        config = self.config()
        config["publication"]["required_credentials"] = ["TOKEN"]
        self.release.prepare(self.root, config)
        calls = []
        def command(argv, *, cwd, env=None):
            calls.append(argv)
            return '{"state":"absent"}'
        with self.assertRaisesRegex(ValueError, "credentials"):
            self.release.publish(self.root, config, command_runner=command, process_env={})
        self.assertEqual([["artifact", "1.2.0"]], calls)

    def test_ci_failure_preserves_release_without_advancing_development(self):
        config = self.config(publication_mode="tag-ci")
        prepared = self.release.prepare(self.root, config)
        def command(argv, *, cwd, env=None):
            return '{"state":"absent"}' if argv[0] == "artifact" else '{"state":"failed"}'
        with self.assertRaises(self.release.RecoveryRequired):
            self.release.publish(self.root, config, command_runner=command, process_env={})
        self.assertEqual(prepared.release_sha, self.git("rev-parse", "HEAD"))
        self.assertEqual("VERSION_NAME=1.2.0\n", self.read("gradle.properties"))

    def test_tag_push_failure_after_upload_does_not_republish(self):
        config = self.config()
        self.release.prepare(self.root, config)
        hook = self.remote / "hooks/update"
        hook.write_text('#!/bin/sh\ncase "$1" in refs/tags/*) exit 1;; esac\nexit 0\n')
        hook.chmod(0o755)
        published = []
        def command(argv, *, cwd, env=None):
            if argv[0] == "publish":
                published.append(True)
                return ""
            return '{"state":"published"}' if published else '{"state":"absent"}'
        with self.assertRaises(self.release.RecoveryRequired):
            self.release.publish(self.root, config, command_runner=command, process_env={})
        with self.assertRaises(self.release.RecoveryRequired):
            self.release.publish(self.root, config, command_runner=command, process_env={})
        self.assertEqual([True], published)
        self.assertEqual("VERSION_NAME=1.2.0\n", self.read("gradle.properties"))

    def test_failed_check_restores_unchanged_helper_owned_files(self):
        before = self.snapshot()
        def command(argv, *, cwd, env=None):
            raise RuntimeError("failed check")
        with self.assertRaises(RuntimeError):
            self.release.prepare(self.root, self.config(checks=[["check"]]), command_runner=command)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / "library/api/1.2.0.txt").exists())

    def test_divergent_remote_branch_blocks_before_preparation_writes(self):
        base = self.git("rev-parse", "HEAD")
        self.write("remote-only.txt", "remote change")
        self.git("add", "remote-only.txt")
        self.git("commit", "-m", "Remote branch advance")
        self.git("push", "origin", "main")
        # Create a different descendant in this temporary test repository.
        self.git("checkout", "-B", "main", base)
        self.write("local-only.txt", "local change")
        self.git("add", "local-only.txt")
        self.git("commit", "-m", "Local branch advance")
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.release.prepare(self.root, self.config())
        self.assertEqual(before, self.snapshot())

    def test_cleanup_preserves_check_edits_and_staging(self):
        def command(argv, *, cwd, env=None):
            self.write("gradle.properties", "VERSION_NAME=check-owned\n")
            self.git("add", "gradle.properties")
            raise RuntimeError("check failed after writing")
        with self.assertRaises(RuntimeError):
            self.release.prepare(self.root, self.config(checks=[["check"]]), command_runner=command)
        self.assertEqual("VERSION_NAME=check-owned\n", self.read("gradle.properties"))
        self.assertEqual("gradle.properties", self.git("diff", "--cached", "--name-only"))
        self.assertFalse((self.root / "library/api/1.2.0.txt").exists())

    def test_exported_credentials_are_removed_from_checks_and_verifiers(self):
        config = self.config(publication_mode="tag-ci", checks=[["check"]])
        config["publication"]["required_credentials"] = ["RELEASE_TEST_TOKEN"]
        seen = []
        def command(argv, *, cwd, env=None):
            probe = [sys.executable, "-c", "import os; print('present' if 'RELEASE_TEST_TOKEN' in os.environ else 'absent')"]
            self.assertEqual("absent", self.release.subprocess_command(probe, cwd=cwd, env=env).strip())
            seen.append(argv[0])
            if argv[0] == "artifact":
                return '{"state":"published"}' if seen.count("artifact") > 1 else '{"state":"absent"}'
            return '{"state":"passed"}'
        with patch.dict(os.environ, {"RELEASE_TEST_TOKEN": "synthetic-only"}):
            self.release.prepare(self.root, config, command_runner=command)
            self.release.publish(self.root, config, command_runner=command)
            self.release.recover(self.root, config, command_runner=command)
        self.assertIn("ci", seen)
        self.assertEqual(3, seen.count("artifact"))

    def test_recovery_needs_only_readback_fields_not_next_version_or_publisher(self):
        config = self.config()
        config.pop("next_version")
        config["publication"].pop("mode")
        config["publication"].pop("command")
        before = self.snapshot()
        calls = []
        def command(argv, *, cwd, env=None):
            calls.append(argv)
            return '{"state":"published"}'
        result = self.release.recover(self.root, config, command_runner=command)
        self.assertEqual("published", result["artifact"])
        self.assertEqual("absent", result["remote_tag"])
        self.assertIn(self.git("rev-parse", "HEAD"), result["remote_branch"])
        self.assertEqual([["artifact", "1.2.0"]], calls)
        self.assertEqual(before, self.snapshot())

    def test_cli_rejects_malformed_field_types_without_tracebacks_or_writes(self):
        cases = [{"branch": 123}, {"version_key": 123}, {"api_snapshots": []},
                 {"publication_mode": []}, {"branch": ["main"]}]
        for fields in cases:
            with self.subTest(fields=fields):
                config = self.config()
                if "publication_mode" in fields:
                    config["publication"]["mode"] = fields["publication_mode"]
                else:
                    config.update(fields)
                config_path = self.root.parent / "invalid.json"
                config_path.write_text(json.dumps(config))
                before = self.snapshot()
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--root", str(self.root),
                     "--config", str(config_path), "prepare"],
                    capture_output=True, text=True,
                )
                self.assertEqual(1, result.returncode)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("must be", result.stderr)
                self.assertEqual(before, self.snapshot())

    def test_publication_keeps_exported_credentials_while_artifact_checks_do_not(self):
        config = self.config()
        config["publication"]["required_credentials"] = ["RELEASE_TEST_TOKEN"]
        self.release.prepare(self.root, config)
        published = []
        def command(argv, *, cwd, env=None):
            probe = [sys.executable, "-c", "import os; print('present' if 'RELEASE_TEST_TOKEN' in os.environ else 'absent')"]
            observed = self.release.subprocess_command(probe, cwd=cwd, env=env).strip()
            if argv[0] == "publish":
                self.assertEqual("present", observed)
                published.append(True)
                return ""
            self.assertEqual("absent", observed)
            return '{"state":"published"}' if published else '{"state":"absent"}'
        with patch.dict(os.environ, {"RELEASE_TEST_TOKEN": "synthetic-only"}):
            self.release.publish(self.root, config, command_runner=command)
        self.assertEqual([True], published)

    def test_release_preserves_crlf_through_preparation_and_next_version(self):
        originals = {}
        for name in ["gradle.properties", "CHANGELOG.md", "library/api/api.txt"]:
            path = self.root / name
            originals[name] = path.read_bytes().replace(b"\n", b"\r\n")
            path.write_bytes(originals[name])
        self.git("add", ".")
        self.git("commit", "-m", "CRLF release fixture")
        config = self.config()
        self.release.prepare(self.root, config)
        self.assertEqual(b"VERSION_NAME=1.2.0\r\n", (self.root / "gradle.properties").read_bytes())
        expected = originals["CHANGELOG.md"].replace(
            b"## Unreleased", b'## Unreleased\r\n\r\n## 1.2.0 <small>2026-09-06</small> { id="1.2.0" }', 1)
        self.assertEqual(expected, (self.root / "CHANGELOG.md").read_bytes())
        self.assertEqual(originals["library/api/api.txt"], (self.root / "library/api/1.2.0.txt").read_bytes())
        published = []
        def command(argv, *, cwd, env=None):
            if argv[0] == "publish":
                published.append(True)
                return ""
            return '{"state":"published"}' if published else '{"state":"absent"}'
        self.release.publish(self.root, config, command_runner=command, process_env={})
        self.assertEqual(b"VERSION_NAME=1.3.0-SNAPSHOT\r\n", (self.root / "gradle.properties").read_bytes())
        self.assertEqual(expected, (self.root / "CHANGELOG.md").read_bytes())

    def test_release_date_rejects_alternative_iso_forms_before_writes(self):
        before = self.snapshot()
        for value in ["20260906", "2026-W36-7", "2026-02-30", "2026-9-6"]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
                    self.release.prepare(self.root, self.config(release_date=value))
                self.assertEqual(before, self.snapshot())
                self.assertFalse((self.root / "library/api/1.2.0.txt").exists())

    def test_tag_ci_ignores_local_dotenv_and_local_publication_credentials(self):
        config = self.config(publication_mode="tag-ci")
        config["publication"]["required_credentials"] = ["CI_ONLY_TOKEN"]
        Path(config["env_file"]).write_text("not a dotenv assignment\n")
        self.release.prepare(self.root, config)
        calls = []
        def command(argv, *, cwd, env=None):
            self.assertNotIn("CI_ONLY_TOKEN", env)
            calls.append(argv[0])
            if argv[0] == "ci":
                return '{"state":"passed"}'
            return '{"state":"published"}' if calls.count("artifact") > 1 else '{"state":"absent"}'
        result = self.release.publish(self.root, config, command_runner=command, process_env={})
        self.assertTrue(result.completed)
        self.assertEqual(["artifact", "ci", "artifact"], calls)
        self.assertEqual("VERSION_NAME=1.3.0-SNAPSHOT\n", self.read("gradle.properties"))

    def config(self, **overrides):
        config = {
            "release_version": "1.2.0",
            "next_version": "1.3.0-SNAPSHOT",
            "version_file": "gradle.properties",
            "version_key": "VERSION_NAME",
            "branch": "main",
            "remote": "origin",
            "tag": "1.2.0",
            "release_date": "2026-09-06",
            "env_file": str(self.root.parent / "missing-release.env"),
            "changelog": {
                "path": "CHANGELOG.md",
                "unreleased_heading": "## Unreleased",
                "release_heading": "## {version} <small>{date}</small> { id=\"{version}\" }",
            },
            "api_snapshots": "haze-published",
            "checks": [],
            "publication": {
                "mode": "local",
                "command": ["publish"],
                "artifact_check": ["artifact", "{release_version}"],
                "required_credentials": [],
            },
        }
        for key, value in overrides.items():
            if key == "changelog":
                config[key] = value
            elif key == "publication_mode":
                config["publication"] = dict(config["publication"], mode=value)
                if value == "tag-ci":
                    config["publication"].pop("command")
                    config["publication"]["ci_check"] = ["ci", "{release_version}"]
            elif key == "env_file":
                config["env_file"] = str(value)
            else:
                config[key] = value
        return config

    def git(self, *args):
        result = subprocess.run(
            ["git", *args], cwd=self.root, check=True, text=True, capture_output=True
        )
        return result.stdout.strip()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8")

    def snapshot(self):
        return (self.git("status", "--porcelain"), self.git("rev-parse", "HEAD"), self.read("gradle.properties"), self.read("CHANGELOG.md"))


if __name__ == "__main__":
    unittest.main()
