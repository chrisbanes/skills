#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


_KOTLIN_NON_CODE = re.compile(
    r'""".*?"""|/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])\'',
    re.DOTALL,
)
_TEST_FUNCTION = re.compile(
    r"@Test\b.*?\bfun\s+\w+\s*\([^)]*\)\s*(?::\s*[^\n{=]+)?\s*\{",
    re.DOTALL,
)


def _kotlin_code(source: str) -> str:
    return _KOTLIN_NON_CODE.sub(lambda match: "\n" * match.group().count("\n"), source)


def _matching_brace(code: str, opening_index: int) -> int | None:
    depth = 0
    for index, character in enumerate(code[opening_index:], start=opening_index):
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _test_bodies(code: str) -> list[str]:
    bodies: list[str] = []
    for match in _TEST_FUNCTION.finditer(code):
        opening_index = match.end() - 1
        closing_index = _matching_brace(code, opening_index)
        if closing_index is not None:
            bodies.append(code[opening_index + 1 : closing_index])
    return bodies


def _call_arguments(body: str, name: str) -> list[str]:
    arguments: list[str] = []
    call_pattern = re.compile(rf"\b{re.escape(name)}\s*\(")
    for match in call_pattern.finditer(body):
        opening_index = body.find("(", match.start())
        closing_index = _matching_parenthesis(body, opening_index)
        if closing_index is not None:
            arguments.append(body[opening_index + 1 : closing_index])
    return arguments


def _matching_parenthesis(code: str, opening_index: int) -> int | None:
    depth = 0
    for index, character in enumerate(code[opening_index:], start=opening_index):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _has_named_arguments(arguments: str, expected: dict[str, str]) -> bool:
    return all(
        re.search(rf"\b{re.escape(name)}\s*=\s*{re.escape(value)}\b", arguments)
        for name, value in expected.items()
    )


def _has_test_call(code: str, expected: dict[str, object]) -> bool:
    name = expected["name"]
    arguments = expected["arguments"]
    if not isinstance(name, str) or not isinstance(arguments, dict):
        return False
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in arguments.items()):
        return False
    return any(
        _has_named_arguments(call, arguments)
        for body in _test_bodies(code)
        for call in _call_arguments(body, name)
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: compose_case.py <case-id>", file=sys.stderr)
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
    kotlin_code = _kotlin_code(subject)
    failures: list[str] = []
    for required in expectations.get("must_contain", []):
        if required not in subject:
            failures.append(f"missing required evidence: {required!r}")
    for relative, required_values in expectations.get("must_contain_by_file", {}).items():
        path = workspace / relative
        if not path.is_file():
            failures.append(f"missing subject file: {relative}")
            continue
        contents = path.read_text(encoding="utf-8")
        for required in required_values:
            if required not in contents:
                failures.append(
                    f"missing required evidence in {relative}: {required!r}"
                )
    for relative, expected_content in expectations.get("exact_content_by_file", {}).items():
        path = workspace / relative
        if not path.is_file():
            failures.append(f"missing subject file: {relative}")
        elif path.read_text(encoding="utf-8").strip() != expected_content.strip():
            failures.append(f"unexpected content in {relative}")
    for alternatives in expectations.get("must_contain_any", []):
        if not any(alternative in subject for alternative in alternatives):
            failures.append(f"missing one of: {alternatives!r}")
    for required, count in expectations.get("minimum_occurrences", {}).items():
        actual = subject.count(required)
        if actual < count:
            failures.append(
                f"expected at least {count} occurrences of {required!r}, found {actual}"
            )
    required_test_call = expectations.get("required_test_call")
    if required_test_call is not None and not _has_test_call(kotlin_code, required_test_call):
        failures.append("missing required test call")
    forbidden_test_call = expectations.get("forbidden_test_call")
    if forbidden_test_call is not None and _has_test_call(kotlin_code, forbidden_test_call):
        failures.append("forbidden test call remains")
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
