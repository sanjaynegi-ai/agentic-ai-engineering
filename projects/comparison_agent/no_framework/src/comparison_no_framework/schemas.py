from typing import Any, Literal
from pydantic import BaseModel, Field

class AgentConfig(BaseModel):
    max_steps: int = Field(default=8, ge=1, le=20)
    max_tool_calls: int = Field(default=10, ge=0, le=30)
    max_input_chars: int = Field(default=4000, ge=1)
class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
class ToolCallResult(BaseModel):
    name: str
    ok: bool
    output: Any
class FinalAnswer(BaseModel):
    answer: str
    estimated_budget_inr: int | None = None
    sources: list[str] = Field(default_factory=list)
class AgentEvent(BaseModel):
    type: Literal["decision", "tool", "guardrail", "stop", "final"]
    detail: str
    step: int = 0
class WeatherResult(BaseModel):
    city: str
    summary: str
    umbrella_recommended: bool
    live: bool = False
class CalculationResult(BaseModel):
    expression: str
    value: float
class TimeResult(BaseModel):
    timezone: str
    iso_time: str
class SearchResult(BaseModel):
    query: str
    matches: list[str]
