from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, TypeVar


class FingerprintMismatch(ValueError):
    """Raised when a persisted result belongs to another experiment."""


T = TypeVar("T")


def result_fingerprint(
    *,
    case_digest: str,
    arm: str,
    skill_sha: str,
    codex_version: str,
    model: str,
    reasoning: str,
    judge_model: str | None = None,
    judge_reasoning: str | None = None,
    skill_catalog_digest: str | None = None,
) -> str:
    fields = {
        "arm": arm,
        "case_digest": case_digest,
        "codex_version": codex_version,
        "model": model,
        "reasoning": reasoning,
        "skill_sha": skill_sha,
    }
    if judge_model is not None:
        fields["judge_model"] = judge_model
    if judge_reasoning is not None:
        fields["judge_reasoning"] = judge_reasoning
    if skill_catalog_digest is not None:
        fields["skill_catalog_digest"] = skill_catalog_digest
    encoded = json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def write_result(path: Path, fingerprint: str, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    document = {"fingerprint": fingerprint, "payload": payload}
    with temporary.open("w", encoding="utf-8") as output:
        json.dump(document, output, indent=2, sort_keys=True)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)


def load_result(path: Path, fingerprint: str) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("fingerprint") != fingerprint:
        raise FingerprintMismatch(f"result fingerprint mismatch: {path}")
    payload = document.get("payload")
    if not isinstance(payload, dict):
        raise ValueError(f"result payload must be an object: {path}")
    return payload


def run_with_one_retry(
    operation: Callable[[], T], retryable: Callable[[T], bool]
) -> tuple[T, int]:
    result = operation()
    if not retryable(result):
        return result, 0
    return operation(), 1
