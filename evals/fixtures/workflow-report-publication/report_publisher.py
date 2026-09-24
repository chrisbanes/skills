from __future__ import annotations

import json
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
    _, published_mount = configured_mounts()
    published = published_mount / f"{report_id}.report"
    published.write_bytes(contents)
    mark_published(report_id)
    return published
