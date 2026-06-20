from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ExpectedBehavior(BaseModel):
    status: Literal["completed", "refused"]
    required_tools: list[str] = Field(default_factory=list)
    required_tool_arguments: dict[str, dict[str, Any]] = Field(default_factory=dict)
    forbidden_tools: list[str] = Field(default_factory=list)
    required_terms: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    max_tool_calls: int = Field(default=8, ge=0)
    max_budget_inr: int | None = Field(default=None, ge=0)


class EvalCase(BaseModel):
    id: str
    category: str
    input: str
    description: str
    expected: ExpectedBehavior


class ToolCallTrace(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentRun(BaseModel):
    case_id: str
    implementation: Literal["no_framework", "openai_agents_sdk"]
    status: Literal["completed", "refused", "error"]
    final_answer: str = ""
    structured_output: dict[str, Any] = Field(default_factory=dict)
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
    handoffs: list[str] = Field(default_factory=list)
    steps: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0, ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    error: str | None = None


class CheckResult(BaseModel):
    name: str
    passed: bool
    detail: str


class CaseGrade(BaseModel):
    case_id: str
    implementation: str
    passed: bool
    score: float = Field(ge=0, le=1)
    checks: list[CheckResult]


class EvaluationReport(BaseModel):
    mode: Literal["offline", "live"]
    cases: int
    runs: list[AgentRun]
    grades: list[CaseGrade]
    summary: dict[str, float]
