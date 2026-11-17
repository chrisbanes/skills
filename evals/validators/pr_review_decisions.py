"""Grade offline PR decisions against evaluator-owned scenario answers.

This validates a subject's decision artifact or response, not live provider capabilities or
execution. The expected answers stay outside the subject workspace.
"""

import json
import sys
from pathlib import Path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def validate_decisions(actual, expected):
    if not isinstance(actual, dict) or actual.keys() != expected.keys():
        return ["decision scenario IDs must match the supplied snapshots"]
    failures = []
    for scenario, fields in expected.items():
        decision = actual[scenario]
        if not isinstance(decision, dict) or decision.keys() != fields.keys():
            failures.append(f"{scenario}: decision fields must match the requested format")
            continue
        for field, value in fields.items():
            # JSON comparison keeps booleans distinct from integers.
            if json.dumps(decision[field], sort_keys=True) != json.dumps(value, sort_keys=True):
                failures.append(f"{scenario}: incorrect {field}")
    return failures


def main(argv):
    response_mode = len(argv) == 3 and argv[2] == "--response"
    if len(argv) != 2 and not response_mode:
        print("usage: pr_review_decisions.py <case-id> [--response]", file=sys.stderr)
        return 2
    cases = Path(__file__).resolve().parents[1] / "cases"
    case = cases / argv[1]
    if case.parent != cases:
        return 2
    try:
        expected = json.loads((case / "expectations.json").read_text(encoding="utf-8"))
        if response_mode:
            output = json.load(sys.stdin, object_pairs_hook=unique_object)
            actual = json.loads(output["summary"], object_pairs_hook=unique_object)
        else:
            actual = json.loads(
                (Path.cwd() / ".scratch/review-decisions.json").read_text(encoding="utf-8"),
                object_pairs_hook=unique_object,
            )
        failures = validate_decisions(actual, expected["decisions"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"cannot read review decisions: {error}", file=sys.stderr)
        return 1
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"validated {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
