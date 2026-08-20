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
    subject = "\n".join(contents)
    failures: list[str] = []
    for pattern in expectations.get("must_match", []):
        if re.search(pattern, subject, re.MULTILINE | re.DOTALL) is None:
            failures.append(f"missing required pattern: {pattern!r}")
    for pattern in expectations.get("must_not_match", []):
        if re.search(pattern, subject, re.MULTILINE | re.DOTALL) is not None:
            failures.append(f"forbidden pattern remains: {pattern!r}")
    for required in expectations.get("must_contain", []):
        if required not in subject:
            failures.append(f"missing required evidence: {required!r}")
    for forbidden in expectations.get("must_not_contain", []):
        if forbidden in subject:
            failures.append(f"forbidden evidence remains: {forbidden!r}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"validated {case_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
