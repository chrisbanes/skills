from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path


CONFIG_PATH = Path(__file__).with_name("report_config.json")


def configured_mounts() -> tuple[Path, Path]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return Path(config["staging_mount"]), Path(config["published_mount"])


def publish_report(
    report_id: str,
    contents: bytes,
    mark_published: Callable[[str], None],
) -> Path:
    staging_mount, published_mount = configured_mounts()
    staged = staging_mount / f"{report_id}.tmp"
    published = published_mount / f"{report_id}.report"
    staged.write_bytes(contents)
    os.replace(staged, published)
    mark_published(report_id)
    return published
