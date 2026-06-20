from __future__ import annotations

from collections.abc import Callable

from .models import AgentRun, CaseGrade, CheckResult, EvalCase


def _check(name: str, passed: bool, detail: str) -> CheckResult:
    return CheckResult(name=name, passed=passed, detail=detail)


def _status(case: EvalCase, run: AgentRun) -> CheckResult:
    expected = case.expected.status
    return _check("status", run.status == expected, f"expected={expected}; actual={run.status}")


def _required_tools(case: EvalCase, run: AgentRun) -> CheckResult:
    actual = {call.name for call in run.tool_calls}
    missing = set(case.expected.required_tools) - actual
    return _check("required_tools", not missing, f"missing={sorted(missing)}; actual={sorted(actual)}")


def _forbidden_tools(case: EvalCase, run: AgentRun) -> CheckResult:
    actual = {call.name for call in run.tool_calls}
    used = set(case.expected.forbidden_tools) & actual
    return _check("forbidden_tools", not used, f"forbidden_used={sorted(used)}")


def _tool_arguments(case: EvalCase, run: AgentRun) -> CheckResult:
    failures: list[str] = []
    for tool_name, expected_arguments in case.expected.required_tool_arguments.items():
        matching_calls = [call for call in run.tool_calls if call.name == tool_name]
        matched = any(
            all(call.arguments.get(key) == value for key, value in expected_arguments.items())
            for call in matching_calls
        )
        if not matched:
            failures.append(f"{tool_name}{expected_arguments}")
    return _check("tool_arguments", not failures, f"unmatched={failures}")


def _tool_budget(case: EvalCase, run: AgentRun) -> CheckResult:
    count = len(run.tool_calls)
    limit = case.expected.max_tool_calls
    return _check("tool_budget", count <= limit, f"calls={count}; limit={limit}")


def _required_terms(case: EvalCase, run: AgentRun) -> CheckResult:
    answer = run.final_answer.casefold()
    missing = [term for term in case.expected.required_terms if term.casefold() not in answer]
    return _check("required_terms", not missing, f"missing={missing}")


def _forbidden_claims(case: EvalCase, run: AgentRun) -> CheckResult:
    answer = run.final_answer.casefold()
    found = [claim for claim in case.expected.forbidden_claims if claim.casefold() in answer]
    return _check("forbidden_claims", not found, f"found={found}")


def _budget(case: EvalCase, run: AgentRun) -> CheckResult:
    limit = case.expected.max_budget_inr
    if limit is None or run.status != "completed":
        return _check("budget", True, "not applicable")
    actual = run.structured_output.get("estimated_budget_inr")
    valid = isinstance(actual, int | float) and actual <= limit
    return _check("budget", valid, f"estimated={actual}; limit={limit}")


GRADERS: tuple[Callable[[EvalCase, AgentRun], CheckResult], ...] = (
    _status,
    _required_tools,
    _forbidden_tools,
    _tool_arguments,
    _tool_budget,
    _required_terms,
    _forbidden_claims,
    _budget,
)


def grade_run(case: EvalCase, run: AgentRun) -> CaseGrade:
    checks = [grader(case, run) for grader in GRADERS]
    score = sum(check.passed for check in checks) / len(checks)
    return CaseGrade(
        case_id=case.id,
        implementation=run.implementation,
        passed=all(check.passed for check in checks),
        score=score,
        checks=checks,
    )
