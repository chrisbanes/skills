#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.harness.cases import CaseValidationError, validate_corpus
from evals.harness.codex import ARMS, RunConfig
from evals.harness.experiment import (
    default_output_dir,
    execute_experiment,
    experiment_plan,
    filter_cases,
    load_raw_records,
    regrade_records,
    rejudge_packets,
    write_rejudged_reports,
)
from evals.harness.judge import JudgeConfig
from evals.harness.report import append_audit_decision, write_reports
from evals.harness.score import compute_scorecard
from evals.harness.suites import SUITES


def _add_experiment_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--judge-model", required=True)
    parser.add_argument("--judge-reasoning", required=True)
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--skill", action="append", dest="skills")
    parser.add_argument("--suite", choices=sorted(SUITES), default="compose")
    parser.add_argument("--arm", action="append", choices=ARMS)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--subject-cost-per-call-usd", type=float)
    parser.add_argument("--judge-cost-per-call-usd", type=float)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate repository skill suites")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate the committed case corpus")
    validate.add_argument("--allow-incomplete-corpus", action="store_true")
    validate.add_argument("--skill-family")
    validate.add_argument("--suite", choices=sorted(SUITES))
    plan = subparsers.add_parser("plan", help="preview calls without executing models")
    _add_experiment_arguments(plan)
    run = subparsers.add_parser("run", help="preview or execute the full experiment")
    _add_experiment_arguments(run)
    run.add_argument("--execute", action="store_true")
    run.add_argument("--output-dir", type=Path)
    run.add_argument("--codex-executable", default="codex")
    report = subparsers.add_parser("report", help="rebuild reports from raw results")
    report.add_argument("--output-dir", type=Path, required=True)
    report.add_argument("--audit-seed", type=int, default=20260816)
    regrade = subparsers.add_parser(
        "regrade", help="reapply current deterministic grading without model calls"
    )
    regrade.add_argument("--output-dir", type=Path, required=True)
    regrade.add_argument("--audit-seed", type=int, default=20260816)
    rejudged_report = subparsers.add_parser(
        "rejudged-report", help="report valid persisted rejudgments without model calls"
    )
    rejudged_report.add_argument("--output-dir", type=Path, required=True)
    rejudged_report.add_argument("--audit-seed", type=int, default=20260816)
    judge = subparsers.add_parser("judge", help="preview or rejudge persisted packets")
    judge.add_argument("--output-dir", type=Path, required=True)
    judge.add_argument("--judge-model", required=True)
    judge.add_argument("--judge-reasoning", required=True)
    judge.add_argument("--codex-executable", default="codex")
    judge.add_argument("--execute", action="store_true")
    judge.add_argument("--json", action="store_true")
    audit = subparsers.add_parser("audit", help="append a human audit decision")
    audit.add_argument("--output-dir", type=Path, required=True)
    audit.add_argument("--id", required=True)
    audit.add_argument("--decision", required=True)
    audit.add_argument("--rationale", required=True)
    return parser


def _print_plan(plan: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return
    print(
        f"{plan['case_count']} cases × {len(plan['arms'])} arms × "
        f"{plan['repetitions']} repetitions"
    )
    if plan["estimated_cost_usd"] is None:
        print("estimated cost: unavailable (provide both per-call USD assumptions)")
    else:
        print(f"estimated cost: ${plan['estimated_cost_usd']:.2f} USD")
    print(
        f"planned calls: {plan['subject_calls']} subject + {plan['judge_calls']} judge "
        f"= {plan['total_calls']} total"
    )
    print(plan["notice"])


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    if args.command == "validate":
        try:
            report = validate_corpus(
                repo_root,
                allow_incomplete=args.allow_incomplete_corpus,
                family=args.skill_family,
                suite=args.suite,
            )
        except CaseValidationError as error:
            print(error, file=sys.stderr)
            return 1
        print(f"validated {report.case_count} cases")
        for gap in report.missing_coverage:
            print(f"missing: {gap}")
        return 0
    if args.command in {"plan", "run"}:
        if args.repetitions <= 0:
            print("repetitions must be positive", file=sys.stderr)
            return 2
        costs = (args.subject_cost_per_call_usd, args.judge_cost_per_call_usd)
        if any(cost is not None and cost < 0 for cost in costs):
            print("per-call cost assumptions cannot be negative", file=sys.stderr)
            return 2
        if (costs[0] is None) != (costs[1] is None):
            print("provide both subject and judge per-call cost assumptions", file=sys.stderr)
            return 2
        if args.command == "run" and args.execute and costs[0] is None:
            print(
                "live execution requires explicit subject and judge per-call cost assumptions",
                file=sys.stderr,
            )
            return 2
        try:
            report = validate_corpus(repo_root, suite=args.suite)
            cases = filter_cases(report.cases, case_ids=args.case_ids, skills=args.skills)
        except (CaseValidationError, ValueError) as error:
            print(error, file=sys.stderr)
            return 1
        arms = args.arm or list(ARMS)
        execute = args.command == "run" and args.execute
        plan = experiment_plan(
            cases,
            arms=arms,
            repetitions=args.repetitions,
            model=args.model,
            reasoning=args.reasoning,
            judge_model=args.judge_model,
            judge_reasoning=args.judge_reasoning,
            execute=execute,
            subject_cost_per_call_usd=costs[0],
            judge_cost_per_call_usd=costs[1],
        )
        _print_plan(plan, args.json)
        if not execute:
            return 0
        output_dir = (args.output_dir or default_output_dir(repo_root)).resolve()
        paths = execute_experiment(
            repo_root,
            cases,
            arms=arms,
            repetitions=args.repetitions,
            run_config=RunConfig(args.model, args.reasoning),
            judge_config=JudgeConfig(args.judge_model, args.judge_reasoning),
            output_dir=output_dir,
            codex_executable=args.codex_executable,
        )
        print(f"results: {paths['results']}")
        print(f"scorecard: {paths['scorecard']}")
        return 0
    if args.command == "report":
        output_dir = args.output_dir.resolve()
        try:
            records = load_raw_records(output_dir)
            if not records:
                print(f"no raw results under {output_dir}", file=sys.stderr)
                return 1
            paths = write_reports(
                output_dir,
                records,
                compute_scorecard(records),
                seed=args.audit_seed,
            )
        except (OSError, ValueError) as error:
            print(error, file=sys.stderr)
            return 1
        print(paths["scorecard"])
        return 0
    if args.command == "regrade":
        output_dir = args.output_dir.resolve()
        try:
            records = load_raw_records(output_dir)
            if not records:
                print(f"no raw results under {output_dir}", file=sys.stderr)
                return 1
            corpus = validate_corpus(repo_root)
            paths = regrade_records(
                repo_root,
                corpus.cases,
                output_dir,
                records,
                audit_seed=args.audit_seed,
            )
        except (CaseValidationError, OSError, ValueError) as error:
            print(error, file=sys.stderr)
            return 1
        print(paths["scorecard"])
        return 0
    if args.command == "rejudged-report":
        output_dir = args.output_dir.resolve()
        try:
            records = load_raw_records(output_dir)
            if not records:
                print(f"no raw results under {output_dir}", file=sys.stderr)
                return 1
            paths = write_rejudged_reports(
                output_dir,
                records,
                audit_seed=args.audit_seed,
            )
        except (OSError, ValueError) as error:
            print(error, file=sys.stderr)
            return 1
        print(paths["scorecard"])
        return 0
    if args.command == "judge":
        result = rejudge_packets(
            repo_root,
            args.output_dir.resolve(),
            JudgeConfig(args.judge_model, args.judge_reasoning),
            execute=args.execute,
            codex_executable=args.codex_executable,
        )
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(
                f"{result['packet_count']} persisted packets; "
                f"{result['judge_calls']} planned judge calls"
            )
        return 0
    if args.command == "audit":
        path = args.output_dir.resolve() / "audit-decisions.jsonl"
        append_audit_decision(path, args.id, args.decision, args.rationale)
        print(path)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
