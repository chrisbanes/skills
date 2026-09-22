#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def validate_task_graph(
    subject: str, rules: dict[str, object], label: str = "subject"
) -> list[str]:
    failures: list[str] = []
    slices = re.findall(
        r"(?ms)^#{3,4}\s+\d+\.\s+.*?\n(.*?)(?=^#{3,4}\s+\d+\.\s+|\Z)",
        subject,
    )
    if not slices:
        return [f"{label}: task graph has no numbered implementation slices"]

    tasks: dict[str, set[str]] = {}
    for number, body in enumerate(slices, start=1):
        ids = re.findall(r"^\*\*Task ID:\*\*\s*`([^`]+)`\s*$", body, re.MULTILINE)
        dependencies = re.findall(
            r"^\*\*Depends on:\*\*\s*(.*?)\s*$", body, re.MULTILINE
        )
        if len(ids) != 1 or len(dependencies) != 1:
            failures.append(
                f"{label}: slice {number} must declare exactly one Task ID and Depends on list"
            )
            continue

        task_id = ids[0]
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id) is None:
            failures.append(f"{label}: invalid task ID {task_id!r}")
            continue
        if task_id in tasks:
            failures.append(f"{label}: duplicate task ID {task_id!r}")
            continue

        raw_dependencies = dependencies[0]
        if raw_dependencies == "`none`":
            dependency_ids: list[str] = []
        else:
            dependency_ids = re.findall(
                r"`([A-Za-z0-9][A-Za-z0-9._-]*)`", raw_dependencies
            )
            expected_text = ", ".join(f"`{item}`" for item in dependency_ids)
            if not dependency_ids or raw_dependencies != expected_text:
                failures.append(
                    f"{label}: malformed dependency list for task {task_id!r}"
                )
                continue
        if len(set(dependency_ids)) != len(dependency_ids):
            failures.append(f"{label}: task {task_id!r} repeats a dependency")
        tasks[task_id] = set(dependency_ids)

    for task_id, dependencies in tasks.items():
        for dependency in dependencies:
            if dependency not in tasks:
                failures.append(
                    f"{label}: task {task_id!r} depends on undeclared task {dependency!r}"
                )

    required_edges = rules.get("required_edges", [])
    if not isinstance(required_edges, list):
        return failures + [f"{label}: task_graph.required_edges must be a list"]
    for edge in required_edges:
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or not all(isinstance(item, str) for item in edge)
        ):
            failures.append(
                f"{label}: task_graph.required_edges entries must be [task, dependency] pairs"
            )
            continue
        task_id, dependency = edge
        if dependency not in tasks.get(task_id, set()):
            failures.append(
                f"{label}: missing required dependency edge {task_id!r} -> {dependency!r}"
            )

    if rules.get("require_acyclic", False):
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> bool:
            if task_id in visiting:
                return False
            if task_id in visited:
                return True
            visiting.add(task_id)
            for dependency in tasks.get(task_id, set()):
                if dependency in tasks and not visit(dependency):
                    return False
            visiting.remove(task_id)
            visited.add(task_id)
            return True

        if any(not visit(task_id) for task_id in tasks):
            failures.append(f"{label}: task dependency graph contains a cycle")
    return failures


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
            subject = path.read_text(encoding="utf-8")
            label = str(path.relative_to(workspace))
            validate_subject(subject, rule, label)
            graph_rules = expectations.get("task_graph")
            if graph_rules is not None:
                if not isinstance(graph_rules, dict):
                    print("task_graph expectation must be an object", file=sys.stderr)
                    return 2
                failures.extend(validate_task_graph(subject, graph_rules, label))
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"validated {case_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
