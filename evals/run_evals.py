from __future__ import annotations

import argparse
import asyncio
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.adapters import require_live_key, run_no_framework, run_openai_agents_sdk
from evals.graders import grade_run
from evals.io import load_cases, load_runs, write_report
from evals.models import AgentRun, EvaluationReport


DATA = ROOT / "evals/data/travel_planning_cases.jsonl"
FIXTURES = {
    "no_framework": ROOT / "evals/fixtures/no_framework_runs.jsonl",
    "openai_agents_sdk": ROOT / "evals/fixtures/openai_agents_sdk_runs.jsonl",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate both travel-agent implementations")
    parser.add_argument("--mode", choices=("offline", "live"), default="offline")
    parser.add_argument(
        "--implementation",
        choices=("all", "no_framework", "openai_agents_sdk"),
        default="all",
    )
    parser.add_argument("--fail-under", type=float, default=1.0)
    parser.add_argument("--output", type=Path, default=ROOT / "evals/reports/latest.json")
    return parser.parse_args()


async def live_runs(implementations: list[str], cases) -> list[AgentRun]:
    require_live_key()
    runs: list[AgentRun] = []
    for case in cases:
        if "no_framework" in implementations:
            runs.append(run_no_framework(case))
        if "openai_agents_sdk" in implementations:
            runs.append(await run_openai_agents_sdk(case))
    return runs


def render(report: EvaluationReport) -> None:
    table = Table(title=f"Agent evaluation ({report.mode})")
    table.add_column("Implementation")
    table.add_column("Case")
    table.add_column("Result")
    table.add_column("Score", justify="right")
    for grade in report.grades:
        result = "PASS" if grade.passed else "FAIL"
        table.add_row(grade.implementation, grade.case_id, result, f"{grade.score:.0%}")
    Console().print(table)
    for implementation, score in report.summary.items():
        Console().print(f"{implementation}: {score:.1%}")


async def main() -> int:
    load_dotenv(ROOT / ".env")
    args = parse_args()
    implementations = list(FIXTURES) if args.implementation == "all" else [args.implementation]
    cases = load_cases(DATA)
    by_id = {case.id: case for case in cases}
    if args.mode == "offline":
        runs = [run for name in implementations for run in load_runs(FIXTURES[name])]
    else:
        runs = await live_runs(implementations, cases)
    grades = [grade_run(by_id[run.case_id], run) for run in runs]
    grouped: dict[str, list[float]] = defaultdict(list)
    for grade in grades:
        grouped[grade.implementation].append(grade.score)
    summary = {name: sum(scores) / len(scores) for name, scores in grouped.items()}
    report = EvaluationReport(
        mode=args.mode,
        cases=len(cases),
        runs=runs,
        grades=grades,
        summary=summary,
    )
    write_report(args.output, report)
    render(report)
    return 0 if summary and min(summary.values()) >= args.fail_under else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
