import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.graders import grade_run
from evals.io import load_cases, load_runs
from evals.models import AgentRun


CASES = ROOT / "evals/data/travel_planning_cases.jsonl"


def test_golden_dataset_has_happy_path_and_guardrails() -> None:
    cases = load_cases(CASES)
    categories = {case.category for case in cases}
    assert len(cases) >= 4
    assert {"happy_path", "scope_guardrail", "safety_guardrail"} <= categories


def test_reviewed_offline_fixtures_pass() -> None:
    cases = {case.id: case for case in load_cases(CASES)}
    fixture_paths = [
        ROOT / "evals/fixtures/no_framework_runs.jsonl",
        ROOT / "evals/fixtures/openai_agents_sdk_runs.jsonl",
    ]
    grades = [
        grade_run(cases[run.case_id], run)
        for fixture in fixture_paths
        for run in load_runs(fixture)
    ]
    assert grades
    assert all(grade.passed for grade in grades)


def test_grader_detects_missing_required_tool() -> None:
    case = load_cases(CASES)[0]
    run = AgentRun(
        case_id=case.id,
        implementation="no_framework",
        status="completed",
        final_answer="Jaipur umbrella budget",
        structured_output={"estimated_budget_inr": 24000},
    )
    grade = grade_run(case, run)
    required_tools = next(check for check in grade.checks if check.name == "required_tools")
    assert required_tools.passed is False
    assert grade.passed is False


def test_grader_detects_wrong_tool_arguments() -> None:
    case = load_cases(CASES)[0]
    fixture = load_runs(ROOT / "evals/fixtures/no_framework_runs.jsonl")[0]
    fixture.tool_calls[1].arguments["city"] = "Delhi"
    grade = grade_run(case, fixture)
    arguments = next(check for check in grade.checks if check.name == "tool_arguments")
    assert arguments.passed is False
