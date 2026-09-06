#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: text_case.py <case-id>", file=sys.stderr)
        return 2
    case_id = argv[1]
    evals_root = Path(__file__).resolve().parents[1]
    expectation_path = evals_root / "cases" / case_id / "expectations.json"
    try:
        expectations = json.loads(expectation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"cannot read expectations for {case_id}: {error}", file=sys.stderr)
        return 2

    workspace = Path.cwd()
    contents: list[str] = []
    for relative in expectations.get("files", []):
        path = workspace / relative
        if not path.is_file():
            print(f"missing subject file: {relative}", file=sys.stderr)
            return 1
        contents.append(path.read_text(encoding="utf-8"))

    failures: list[str] = []

    def validate_subject(subject: str, rules: dict[str, object], label: str) -> None:
        for pattern in rules.get("must_match", []):
            if re.search(pattern, subject, re.MULTILINE | re.DOTALL) is None:
                failures.append(f"{label}: missing required pattern: {pattern!r}")
        for pattern in rules.get("must_not_match", []):
            if re.search(pattern, subject, re.MULTILINE | re.DOTALL) is not None:
                failures.append(f"{label}: forbidden pattern remains: {pattern!r}")
        for required in rules.get("must_contain", []):
            if required not in subject:
                failures.append(f"{label}: missing required evidence: {required!r}")
        for forbidden in rules.get("must_not_contain", []):
            if forbidden in subject:
                failures.append(f"{label}: forbidden evidence remains: {forbidden!r}")

    validate_subject("\n".join(contents), expectations, "subject")
    for rule in expectations.get("file_globs", []):
        pattern = rule.get("pattern") if isinstance(rule, dict) else None
        count = rule.get("count") if isinstance(rule, dict) else None
        if not isinstance(pattern, str) or not isinstance(count, int):
            print("file_globs entries require string pattern and integer count", file=sys.stderr)
            return 2
        matches = sorted(path for path in workspace.glob(pattern) if path.is_file())
        if len(matches) != count:
            failures.append(
                f"file glob {pattern!r}: expected {count} files, found {len(matches)}"
            )
            continue
        for path in matches:
            validate_subject(path.read_text(encoding="utf-8"), rule, str(path.relative_to(workspace)))
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"validated {case_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
