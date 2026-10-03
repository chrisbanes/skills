"""Copy shared references into standalone skills, or check without writing."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIES = {
    "references/subagent-selection.md": tuple(
        f"skills/{skill}/references/subagent-selection.md"
        for skill in (
            "deliver-spec", "implement-with-subagents", "run-github-project",
            "gradle-run", "shepherd",
        )
    ),
    "skills/implement-with-subagents/references/implementation-mode.md": (
        "skills/deliver-spec/references/implementation-mode.md",
    ),
}


def synchronize(root: Path, *, check: bool) -> int:
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
