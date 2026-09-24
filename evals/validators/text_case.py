#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def _mask_fenced_code(subject: str) -> str:
    """Blank fenced code while preserving line breaks and source offsets."""
    masked: list[str] = []
    fence_char: str | None = None
    fence_size = 0

    def blank(line: str) -> str:
        return re.sub(r"[^\r\n]", " ", line)

    for line in subject.splitlines(keepends=True):
        if fence_char is None:
            opening = re.match(r" {0,3}(`{3,}|~{3,})", line)
            if opening:
                fence = opening.group(1)
                fence_char, fence_size = fence[0], len(fence)
                masked.append(blank(line))
                continue
        else:
            closing = re.match(
                rf" {{0,3}}{re.escape(fence_char)}{{{fence_size},}}[ \t]*(?:\r?\n)?$",
                line,
            )
            masked.append(blank(line))
            if closing:
                fence_char = None
                fence_size = 0
            continue
        masked.append(line)
    return "".join(masked)


def _mask_html_comments(subject: str) -> str:
    return re.sub(
        r"<!--.*?(?:-->|$)",
        lambda match: re.sub(r"[^\r\n]", " ", match.group()),
        subject,
        flags=re.DOTALL,
    )


def _mask_inline_code(subject: str) -> str:
    return re.sub(
        r"(?<!`)(`+)(?!`)(.*?)\1(?!`)",
        lambda match: re.sub(r"[^\r\n]", " ", match.group()),
        subject,
        flags=re.DOTALL,
    )


def markdown_bullets_under_heading(subject: str, heading: str) -> list[str]:
    """Collect visible top-level bullets before the next release or details block."""
    lines = subject.splitlines()
    visible_lines = _mask_inline_code(
        _mask_html_comments(_mask_fenced_code(subject))
    ).splitlines()
    bullets: list[str] = []
    current: list[str] = []
    in_section = False
    after_blank = False

    def finish() -> None:
        if current:
            bullets.append("\n".join(current))
            current.clear()

    for original, visible in zip(lines, visible_lines):
        if not in_section:
            if re.fullmatch(rf"##[ \t]+{re.escape(heading)}[ \t]*", visible):
                in_section = True
            continue
        if re.match(r"##[ \t]|<details>", visible):
            finish()
            break
        if re.fullmatch(r"[ \t]*(?:-{3,}|_{3,}|\*{3,})[ \t]*", visible):
            finish()
            continue
        if re.match(r" {0,3}(?:[-+*]|\d+[.)])[ \t]+", visible):
            finish()
            current.append(visible)
            after_blank = False
            continue
        if not current:
            continue
        if not visible.strip():
            if original.strip() and not original.startswith(("  ", "\t")):
                finish()
            elif not original.strip():
                after_blank = True
            continue
        if after_blank and not visible.startswith(("  ", "\t")):
            finish()
            continue
        current.append(visible)
        after_blank = False
    finish()
    return bullets


def validate_task_graph(
    subject: str, rules: dict[str, object], label: str = "subject"
) -> list[str]:
    failures: list[str] = []
    structural_subject = _mask_fenced_code(subject)
    headings = list(
        re.finditer(
            r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$",
            structural_subject,
            re.MULTILINE,
        )
    )
    section_headings = [
        heading
        for heading in headings
        if heading.group(2).strip().casefold() == "implementation slices"
    ]
    if len(section_headings) != 1:
        return [
            f"{label}: expected one Implementation slices section, found {len(section_headings)}"
        ]

    section = section_headings[0]
    section_level = len(section.group(1))
    section_boundary = next(
        (
            heading
            for heading in headings
            if heading.start() > section.start()
            and len(heading.group(1)) <= section_level
        ),
        None,
    )
    section_end = (
        section_boundary.start() if section_boundary else len(structural_subject)
    )
    if (
        section_boundary
        and section_boundary.group(2).strip().casefold() != "acceptance coverage"
    ):
        failures.append(
            f"{label}: unexpected section boundary after Implementation slices: "
            f"{section_boundary.group(2).strip()!r}"
        )
    slice_level = section_level + 1
    section_headings_inside = [
        heading
        for heading in headings
        if section.end() < heading.start() < section_end
    ]
    for heading in section_headings_inside:
        if len(heading.group(1)) != slice_level:
            failures.append(
                f"{label}: unexpected heading level in Implementation slices: {heading.group(2)!r}"
            )
    slice_headings = [
        heading for heading in section_headings_inside if len(heading.group(1)) == slice_level
    ]
    if not slice_headings:
        return [f"{label}: task graph has no implementation slices"]

    tasks: dict[str, set[str]] = {}
    expected_number = 1
    for heading_index, heading in enumerate(slice_headings):
        title = heading.group(2).strip()
        match = re.fullmatch(r"(\d+)\.\s+.+", title)
        if match is None:
            failures.append(
                f"{label}: malformed implementation slice heading {title!r}"
            )
            continue
        if int(match.group(1)) != expected_number:
            failures.append(
                f"{label}: expected implementation slice {expected_number}, found {match.group(1)}"
            )
        expected_number = int(match.group(1)) + 1

        body_start = heading.end()
        body_end = (
            slice_headings[heading_index + 1].start()
            if heading_index + 1 < len(slice_headings)
            else section_end
        )
        body = structural_subject[body_start:body_end]
        ids = re.findall(r"^\*\*Task ID:\*\*\s*`([^`]+)`\s*$", body, re.MULTILINE)
        dependencies = re.findall(
            r"^\*\*Depends on:\*\*\s*(.*?)\s*$", body, re.MULTILINE
        )
        if len(ids) != 1 or len(dependencies) != 1:
            failures.append(
                f"{label}: slice {heading_index + 1} must declare exactly one Task ID and Depends on list"
            )
            continue

        task_id = ids[0]
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", task_id) is None:
            failures.append(f"{label}: invalid task ID {task_id!r}")
            continue
        if task_id.casefold() == "none":
            failures.append(f"{label}: task ID 'none' is reserved for the root dependency marker")
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
            if dependency.casefold() == "none":
                failures.append(
                    f"{label}: task ID 'none' is reserved for the root dependency marker"
                )
            elif dependency not in tasks:
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
        bullet_rules = rules.get("markdown_bullets")
        if bullet_rules:
            bullets = markdown_bullets_under_heading(subject, bullet_rules["heading"])
            for patterns in bullet_rules["required"]:
                if not any(
                    all(re.search(pattern, bullet, re.IGNORECASE) for pattern in patterns)
                    for bullet in bullets
                ):
                    failures.append(f"{label}: missing required pattern in a release bullet: {patterns!r}")
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
