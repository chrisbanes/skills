from __future__ import annotations

from dataclasses import dataclass


ROUTER_SKILL = "using-chrisbanes-skills"
PUBLIC_SKILLS = (
    "compose-animations",
    "compose-component-design",
    "compose-focus-navigation",
    "compose-performance",
    "compose-state-and-effects",
    "compose-ui-testing-patterns",
    "gradle-run",
    "implement-with-subagents",
    "kotlin-api-design",
    "kotlin-concurrency-and-flow",
    "kotlin-control-flow",
    "run-github-project",
    "shepherd",
    "to-plan",
    ROUTER_SKILL,
)


@dataclass(frozen=True)
class SuitePolicy:
    id: str
    title: str
    skills: tuple[str, ...]
    benchmark_cases: int
    routing_cases: int
    calibration_cases: int = 0
    topic_triads: tuple[tuple[str, str], ...] = ()
    require_skill_triads: bool = False
    historical_minimum: int = 0


COMPOSE_SKILLS = (
    "compose-state-and-effects",
    "compose-performance",
    "compose-component-design",
    "compose-animations",
    "compose-focus-navigation",
    "compose-ui-testing-patterns",
)
COMPOSE_TOPICS = (
    ("compose-state-authoring", "compose-state-and-effects"),
    ("compose-state-hoisting", "compose-state-and-effects"),
    ("compose-side-effects", "compose-state-and-effects"),
    ("compose-recomposition-performance", "compose-performance"),
    ("compose-stability-diagnostics", "compose-performance"),
    ("compose-state-deferred-reads", "compose-performance"),
    ("compose-modifier-and-layout-style", "compose-component-design"),
    ("compose-slot-api-pattern", "compose-component-design"),
    ("compose-animations", "compose-animations"),
    ("compose-focus-navigation", "compose-focus-navigation"),
    ("compose-ui-testing-patterns", "compose-ui-testing-patterns"),
)
KOTLIN_GRADLE_SKILLS = (
    "gradle-run",
    "kotlin-api-design",
    "kotlin-concurrency-and-flow",
    "kotlin-control-flow",
)


SUITES = {
    "compose": SuitePolicy(
        id="compose",
        title="Compose",
        skills=COMPOSE_SKILLS,
        benchmark_cases=38,
        routing_cases=5,
        calibration_cases=4,
        topic_triads=COMPOSE_TOPICS,
    ),
    "kotlin-gradle": SuitePolicy(
        id="kotlin-gradle",
        title="Kotlin and Gradle",
        skills=KOTLIN_GRADLE_SKILLS,
        benchmark_cases=19,
        routing_cases=3,
        require_skill_triads=True,
        historical_minimum=3,
    ),
}


def suite_for_skills(skills: tuple[str, ...]) -> SuitePolicy:
    matches = [policy for policy in SUITES.values() if set(skills) <= set(policy.skills)]
    if len(matches) != 1:
        raise ValueError(f"skills do not belong to exactly one evaluation suite: {skills}")
    return matches[0]
