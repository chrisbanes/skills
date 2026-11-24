"""Copy shared references into standalone skills, or check without writing."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIES = {
    "references/github-delivery.md": tuple(
        f"skills/{skill}/references/github-delivery.md"
        for skill in ("deliver-issue", "run-project", "to-plan")
    ),
    "references/github-binding.md": (
        "skills/run-project/references/github-binding.md",
        "skills/to-plan/references/github-binding.md",
    ),
    "references/jira-binding.md": tuple(
        f"skills/{skill}/references/jira-binding.md"
        for skill in ("deliver-issue", "run-project", "to-plan")
    ),
    "references/gitlab-binding.md": (
        "skills/deliver-issue/references/gitlab-binding.md",
        "skills/run-project/references/gitlab-binding.md",
        "skills/to-plan/references/gitlab-binding.md",
    ),
    "references/pr-review-timing.md": tuple(
        f"skills/{skill}/references/pr-review-timing.md"
        for skill in ("deliver-issue", "run-project", "shepherd")
    ),
    "skills/to-plan/references/boundary-validation.md": tuple(
        f"skills/{skill}/references/boundary-validation.md"
        for skill in ("deliver-issue", "run-project", "implement-with-subagents")
    ),
    "references/behavioral-review.md": tuple(
        f"skills/{skill}/references/behavioral-review.md"
        for skill in (
            "deliver-issue", "implement-with-subagents", "run-project",
            "shepherd",
        )
    ),
    "references/subagent-selection.md": tuple(
        f"skills/{skill}/references/subagent-selection.md"
        for skill in (
            "deliver-issue", "implement-with-subagents", "run-project",
            "gradle-run", "shepherd", "subagent-delegation",
        )
    ),
    "references/checkout-lifecycle.md": tuple(
        f"skills/{skill}/references/checkout-lifecycle.md"
        for skill in ("deliver-issue", "implement-with-subagents", "run-project")
    ),
    "skills/run-project/references/review-contracts.md": ("skills/deliver-issue/references/review-contracts.md",),
    "skills/deliver-issue/references/issue-lifecycle.md": ("skills/run-project/references/issue-lifecycle.md",),
    "skills/deliver-issue/references/delivery-lifecycle.md": ("skills/run-project/references/delivery-lifecycle.md",),
    "skills/deliver-issue/references/evidence-and-review.md": ("skills/run-project/references/evidence-and-review.md",),
    "skills/deliver-issue/references/fast-path.md": ("skills/run-project/references/fast-path.md",),
    "skills/deliver-issue/references/implementation-mode.md": ("skills/run-project/references/implementation-mode.md",),
    "skills/deliver-issue/references/project-handoff.md": ("skills/run-project/references/project-handoff.md",),
    "skills/deliver-issue/references/provider-bindings.md": ("skills/run-project/references/provider-bindings.md",),
    "skills/deliver-issue/references/qualification-failure.md": ("skills/run-project/references/qualification-failure.md",),
}


# The planner still bundles the Project binding and its board procedures.
for name in (
    "agent-routing", "authority-and-pauses", "drain-scheduler", "execution-controller",
    "human-frontier", "normalized-ticket", "review-and-setup", "ticket-lifecycle",
    "todo-lane", "triage-lane", "wayfinder-lane", "workflow-providers",
):
    COPIES[f"skills/run-project/references/{name}.md"] = (f"skills/to-plan/references/{name}.md",)


# The shared binding links to these procedures; retain its reference closure
# when the planner is installed without either delivery entrypoint.
for source, destinations in tuple(COPIES.items()):
    if any("/references/" in path and ("/run-project/" in path or "/deliver-issue/" in path) for path in destinations):
        planner_copy = "skills/to-plan/references/" + Path(source).name
        if source != planner_copy and planner_copy not in destinations:
            COPIES[source] = (*destinations, planner_copy)


def synchronize(root: Path, *, check: bool) -> int:
    root = root.resolve()
    # Validate every source and destination parent before reading or writing.
    for source, destinations in COPIES.items():
        paths = [root / source, *((root / item).parent for item in destinations)]
        for path in paths:
            if not path.resolve().is_relative_to(root) or any(
                part.is_symlink() for part in (path, *path.parents) if part != root
            ):
                print(f"Refusing symlinked or outside-checkout reference path: {path}")
                return 1
    stale = []
    for source, destinations in COPIES.items():
        content = (root / source).read_bytes()
        for destination in destinations:
            target = root / destination
            if target.is_symlink() or not target.is_file() or target.read_bytes() != content:
                stale.append(destination)
                if not check:
                    if target.is_symlink():
                        target.unlink()
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
    if check and stale:
        print("References out of sync:\n" + "\n".join(stale))
        print("Run npm run references:sync and commit the updated copies.")
        return 1
    print("References are in sync." if check else f"Updated {len(stale)} reference copies.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without writing")
    args = parser.parse_args()
    raise SystemExit(synchronize(ROOT, check=args.check))
