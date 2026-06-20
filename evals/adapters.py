from __future__ import annotations

import os
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

from .models import AgentRun, EvalCase, ToolCallTrace


ROOT = Path(__file__).resolve().parents[1]
NO_FRAMEWORK_SRC = ROOT / "projects/comparison_agent/no_framework/src"
SDK_SRC = ROOT / "projects/comparison_agent/openai_agents_sdk/src"
for source in (NO_FRAMEWORK_SRC, SDK_SRC):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))


def _final_text(output: Any) -> tuple[str, dict[str, Any]]:
    if hasattr(output, "model_dump"):
        structured = output.model_dump(mode="json")
        return str(structured), structured
    return str(output), {}


def run_no_framework(case: EvalCase) -> AgentRun:
    from comparison_no_framework.agent import TravelAgent
    from comparison_no_framework.errors import GuardrailError
    from comparison_no_framework.llm import OpenAILLM
    from comparison_no_framework.tool_registry import ToolRegistry

    class RecordingRegistry(ToolRegistry):
        def __init__(self) -> None:
            super().__init__()
            self.calls: list[ToolCallTrace] = []

        def execute(self, request):
            self.calls.append(ToolCallTrace(name=request.name, arguments=request.arguments))
            return super().execute(request)

    registry = RecordingRegistry()
    started = perf_counter()
    try:
        result = TravelAgent(OpenAILLM(), registry=registry).run(case.input)
        status = "completed"
        text = result.answer
        structured = result.model_dump(mode="json")
        error = None
    except GuardrailError as exc:
        status, text, structured, error = "refused", str(exc), {}, None
    except Exception as exc:
        status, text, structured, error = "error", "", {}, f"{type(exc).__name__}: {exc}"
    return AgentRun(
        case_id=case.id,
        implementation="no_framework",
        status=status,
        final_answer=text,
        structured_output=structured,
        tool_calls=registry.calls,
        steps=len(registry.calls) + 1,
        latency_ms=(perf_counter() - started) * 1000,
        error=error,
    )


async def run_openai_agents_sdk(case: EvalCase) -> AgentRun:
    from agents import InputGuardrailTripwireTriggered, Runner
    from comparison_openai_agents.agents import build_agents

    started = perf_counter()
    tools: list[ToolCallTrace] = []
    handoffs: list[str] = []
    try:
        result = await Runner.run(build_agents()["triage"], input=case.input, max_turns=8)
        for item in result.new_items:
            item_type = type(item).__name__
            raw = getattr(item, "raw_item", None)
            if "ToolCall" in item_type:
                name = getattr(raw, "name", None) or getattr(item, "name", "unknown")
                tools.append(ToolCallTrace(name=str(name)))
            if "Handoff" in item_type:
                target = getattr(item, "target_agent", None)
                handoffs.append(getattr(target, "name", item_type))
        text, structured = _final_text(result.final_output)
        status, error = "completed", None
    except InputGuardrailTripwireTriggered as exc:
        status, text, structured, error = "refused", str(exc), {}, None
    except Exception as exc:
        status, text, structured, error = "error", "", {}, f"{type(exc).__name__}: {exc}"
    return AgentRun(
        case_id=case.id,
        implementation="openai_agents_sdk",
        status=status,
        final_answer=text,
        structured_output=structured,
        tool_calls=tools,
        handoffs=handoffs,
        steps=len(tools) + len(handoffs) + 1,
        latency_ms=(perf_counter() - started) * 1000,
        error=error,
    )


def require_live_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Live evals require OPENAI_API_KEY in the environment or .env file")
