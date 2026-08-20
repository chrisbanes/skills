from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from evals.harness.suites import (
    COMPOSE_SKILLS,
    COMPOSE_TOPICS,
    PUBLIC_SKILLS,
    ROUTER_SKILL,
    SUITES,
    SuitePolicy,
    suite_for_skills,
)


EVALUATED_TOPICS = COMPOSE_TOPICS
TASK_MODES = {"review", "edit"}
CASE_KINDS = {"direct", "novel", "negative", "routing"}
_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class CaseValidationError(ValueError):
    """Raised when a case or corpus cannot produce a trustworthy evaluation."""


@dataclass(frozen=True)
class Validator:
    argv: tuple[str, ...]
    timeout_seconds: int


@dataclass(frozen=True)
class EvalCase:
    id: str
    title: str
    family: str
    target_skills: tuple[str, ...]
    expected_skills: tuple[str, ...]
    task_mode: str
    kind: str
    fixture: str
    allowed_write_paths: tuple[str, ...]
    validators: tuple[Validator, ...]
    rubric: tuple[dict[str, str], ...]
    provenance: dict[str, str]
    prompt: str
    directory: Path
    required_command_patterns: tuple[str, ...] = ()
    forbidden_command_patterns: tuple[str, ...] = ()
    calibration: bool = False


@dataclass(frozen=True)
class CorpusReport:
    cases: tuple[EvalCase, ...]
    missing_coverage: tuple[str, ...]

    @property
    def case_count(self) -> int:
        return len(self.cases)


def _require_string(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise CaseValidationError(f"{field} must be a non-empty string")
    return value


def _require_string_list(data: dict[str, Any], field: str) -> tuple[str, ...]:
    value = data.get(field)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CaseValidationError(f"{field} must be a string array")
    if len(value) != len(set(value)):
        raise CaseValidationError(f"{field} contains duplicates")
    return tuple(value)


def _safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def _validate_provenance(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or value.get("kind") not in {"synthetic", "historical"}:
        raise CaseValidationError("provenance.kind must be synthetic or historical")
    if value["kind"] == "historical":
        for field in ("source_url", "revision", "license", "normalization_note"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                raise CaseValidationError(f"historical provenance requires {field}")
        if not value["source_url"].startswith("https://"):
            raise CaseValidationError("historical provenance source_url must use https")
        if not re.fullmatch(r"[0-9a-f]{40}", value["revision"]):
            raise CaseValidationError(
                "historical provenance revision must be a full lowercase Git SHA"
            )
    return {str(key): str(item) for key, item in value.items()}


def load_case(manifest_path: Path, repo_root: Path) -> EvalCase:
    manifest_path = manifest_path.resolve()
    repo_root = repo_root.resolve()
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CaseValidationError(f"cannot read {manifest_path}: {error}") from error
    if not isinstance(data, dict):
        raise CaseValidationError("case manifest must be a JSON object")

    case_id = _require_string(data, "id")
    if not _ID_PATTERN.fullmatch(case_id):
        raise CaseValidationError("id must be lowercase kebab-case")
    if manifest_path.parent.name != case_id:
        raise CaseValidationError("case id must match its directory name")

    target_skills = _require_string_list(data, "target_skills")
    expected_skills = _require_string_list(data, "expected_skills")
    known_skills = set(PUBLIC_SKILLS) - {ROUTER_SKILL}
    for field, values in (
        ("target_skills", target_skills),
        ("expected_skills", expected_skills),
    ):
        unknown = set(values) - known_skills
        if unknown:
            raise CaseValidationError(f"{field} contains unknown skills: {sorted(unknown)}")
    for skill in set(target_skills) | set(expected_skills):
        if not (repo_root / "skills" / skill / "SKILL.md").is_file():
            raise CaseValidationError(f"missing skill path: skills/{skill}/SKILL.md")

    task_mode = _require_string(data, "task_mode")
    kind = _require_string(data, "kind")
    if task_mode not in TASK_MODES:
        raise CaseValidationError(f"unknown task_mode: {task_mode}")
    if kind not in CASE_KINDS:
        raise CaseValidationError(f"unknown kind: {kind}")
    if kind == "routing" and not expected_skills:
        raise CaseValidationError("routing cases require at least one expected skill")

    fixture = _require_string(data, "fixture")
    if not _safe_relative(fixture):
        raise CaseValidationError("fixture must be a safe relative path")
    if not (repo_root / "evals" / "fixtures" / fixture).is_dir():
        raise CaseValidationError(f"missing fixture: evals/fixtures/{fixture}")

    allowed_write_paths = _require_string_list(data, "allowed_write_paths")
    if task_mode == "review" and allowed_write_paths:
        raise CaseValidationError("review cases cannot declare writable paths")
    for path in allowed_write_paths:
        if not _safe_relative(path):
            raise CaseValidationError(f"unsafe allowed_write_path: {path}")

    raw_validators = data.get("validators")
    if not isinstance(raw_validators, list) or not raw_validators:
        raise CaseValidationError("validators must be a non-empty array")
    validators: list[Validator] = []
    for raw in raw_validators:
        if not isinstance(raw, dict):
            raise CaseValidationError("validator must be an object")
        argv = raw.get("argv")
        timeout = raw.get("timeout_seconds")
        if (
            not isinstance(argv, list)
            or not argv
            or any(not isinstance(arg, str) or not arg for arg in argv)
            or any(not _safe_relative(arg) for arg in argv if "/" in arg)
        ):
            raise CaseValidationError("validator argv must contain safe argument strings")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
            raise CaseValidationError("validator timeout_seconds must be a positive integer")
        validators.append(Validator(tuple(argv), timeout))

    raw_rubric = data.get("rubric")
    if not isinstance(raw_rubric, list) or not raw_rubric:
        raise CaseValidationError("rubric must be a non-empty array")
    rubric: list[dict[str, str]] = []
    rubric_ids: set[str] = set()
    for item in raw_rubric:
        if not isinstance(item, dict):
            raise CaseValidationError("rubric items must be objects")
        rubric_id = item.get("id")
        text = item.get("text")
        if not isinstance(rubric_id, str) or not _ID_PATTERN.fullmatch(rubric_id):
            raise CaseValidationError("rubric id must be lowercase kebab-case")
        if rubric_id in rubric_ids or not isinstance(text, str) or not text.strip():
            raise CaseValidationError("rubric items require unique ids and non-empty text")
        rubric_ids.add(rubric_id)
        rubric.append({"id": rubric_id, "text": text})

    prompt_path = manifest_path.parent / "prompt.md"
    if not prompt_path.is_file():
        raise CaseValidationError("case requires prompt.md")
    prompt = prompt_path.read_text(encoding="utf-8")
    if not prompt.strip():
        raise CaseValidationError("prompt.md cannot be empty")

    calibration = data.get("calibration", False)
    if not isinstance(calibration, bool):
        raise CaseValidationError("calibration must be a boolean")

    command_patterns: dict[str, tuple[str, ...]] = {}
    for field in ("required_command_patterns", "forbidden_command_patterns"):
        patterns = _require_string_list(data, field) if field in data else ()
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as error:
                raise CaseValidationError(f"invalid {field} regex: {pattern}") from error
        command_patterns[field] = patterns

    return EvalCase(
        id=case_id,
        title=_require_string(data, "title"),
        family=_require_string(data, "family"),
        target_skills=target_skills,
        expected_skills=expected_skills,
        task_mode=task_mode,
        kind=kind,
        fixture=fixture,
        allowed_write_paths=allowed_write_paths,
        validators=tuple(validators),
        rubric=tuple(rubric),
        provenance=_validate_provenance(data.get("provenance")),
        calibration=calibration,
        prompt=prompt,
        directory=manifest_path.parent,
        required_command_patterns=command_patterns["required_command_patterns"],
        forbidden_command_patterns=command_patterns["forbidden_command_patterns"],
    )


def _coverage_gaps(policy: SuitePolicy, cases: list[EvalCase]) -> list[str]:
    gaps: list[str] = []
    benchmark_cases = [case for case in cases if not case.calibration]
    by_id = {case.id: case for case in benchmark_cases}
    expected_conditions = (
        ("direct", "edit"),
        ("novel", "review"),
        ("negative", "edit"),
    )
    for topic, skill in policy.topic_triads:
        topic_cases: list[EvalCase] = []
        for kind, task_mode in expected_conditions:
            case_id = f"{topic}-{kind}"
            case = by_id.get(case_id)
            if case is None:
                gaps.append(f"{topic}: missing {task_mode} {kind} case")
                continue
            topic_cases.append(case)
            if case.kind != kind or case.task_mode != task_mode:
                gaps.append(f"{case_id}: expected {task_mode} {kind}")
            if case.target_skills != (skill,) or skill not in case.expected_skills:
                gaps.append(f"{case_id}: expected primary routing to {skill}")
        historical = [case for case in topic_cases if case.provenance["kind"] == "historical"]
        if len(historical) != 1:
            gaps.append(f"{topic}: expected 1 historical case, found {len(historical)}")
    if policy.require_skill_triads:
        for skill in policy.skills:
            skill_cases = [case for case in benchmark_cases if skill in case.target_skills]
            for kind in ("direct", "novel", "negative"):
                if not any(case.kind == kind for case in skill_cases):
                    gaps.append(f"{skill}: missing {kind} case")
    historical_count = sum(
        case.provenance["kind"] == "historical" for case in benchmark_cases
    )
    if historical_count < policy.historical_minimum:
        gaps.append(
            f"provenance: expected at least {policy.historical_minimum} historical cases, "
            f"found {historical_count}"
        )
    routing_count = sum(case.kind == "routing" for case in benchmark_cases)
    if routing_count != policy.routing_cases:
        gaps.append(
            f"{policy.id} router: expected {policy.routing_cases} cases, found {routing_count}"
        )
    if len(benchmark_cases) != policy.benchmark_cases:
        gaps.append(
            f"{policy.id} corpus: expected {policy.benchmark_cases} benchmark cases, "
            f"found {len(benchmark_cases)}"
        )
    calibration_count = sum(case.calibration for case in cases)
    if calibration_count != policy.calibration_cases:
        gaps.append(
            f"{policy.id} calibration: expected {policy.calibration_cases} cases, "
            f"found {calibration_count}"
        )
    return gaps


def validate_corpus(
    repo_root: Path,
    *,
    allow_incomplete: bool = False,
    family: str | None = None,
    suite: str | None = None,
) -> CorpusReport:
    repo_root = repo_root.resolve()
    if not (repo_root / "skills" / ROUTER_SKILL / "SKILL.md").is_file():
        raise CaseValidationError(f"missing router path: skills/{ROUTER_SKILL}/SKILL.md")
    manifest_paths = sorted((repo_root / "evals" / "cases").glob("*/case.json"))
    cases = [load_case(path, repo_root) for path in manifest_paths]
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise CaseValidationError("case ids must be unique")
    by_suite: dict[str, list[EvalCase]] = {suite_id: [] for suite_id in SUITES}
    for case in cases:
        try:
            policy = suite_for_skills(case.target_skills)
        except ValueError as error:
            raise CaseValidationError(str(error)) from error
        by_suite[policy.id].append(case)
    gaps = [
        gap
        for suite_id, policy in SUITES.items()
        for gap in _coverage_gaps(policy, by_suite[suite_id])
    ]
    if suite is not None and suite not in SUITES:
        raise CaseValidationError(f"unknown evaluation suite: {suite}")
    selected = cases if suite is None else by_suite[suite]
    if family is not None:
        selected = [case for case in selected if case.family == family]
    if family is not None and not selected:
        raise CaseValidationError(f"unknown or empty skill family: {family}")
    if gaps and not allow_incomplete:
        raise CaseValidationError("corpus coverage is incomplete:\n- " + "\n- ".join(gaps))
    return CorpusReport(tuple(selected), tuple(gaps))
