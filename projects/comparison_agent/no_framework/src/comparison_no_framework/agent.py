import json
from typing import Protocol
from .errors import AgentLimitError, UnknownToolError
from .guardrails import validate_input, validate_output
from .observability import record
from .schemas import AgentConfig, AgentEvent, FinalAnswer, ToolCallRequest
from .tool_registry import ToolRegistry
class DecisionModel(Protocol):
    def decide(self, messages: list[dict[str, str]]) -> dict: ...
class TravelAgent:
    def __init__(self, llm: DecisionModel, config: AgentConfig | None = None, registry: ToolRegistry | None = None): self.llm, self.config, self.registry = llm, config or AgentConfig(), registry or ToolRegistry()
    def run(self, user_input: str) -> FinalAnswer:
        clean = validate_input(user_input, self.config.max_input_chars); messages = [{"role": "user", "content": clean}]; seen = set(); calls = 0
        for step in range(1, self.config.max_steps + 1):
            decision = self.llm.decide(messages); record(AgentEvent(type="decision", detail=str(decision.get("type")), step=step))
            if decision.get("type") == "final":
                final = FinalAnswer.model_validate(decision.get("final", {})); final.answer = validate_output(final.answer); return final
            if decision.get("type") != "tool": raise UnknownToolError("Decision must be tool or final")
            request = ToolCallRequest.model_validate(decision.get("tool", {})); signature = request.model_dump_json()
            if signature in seen: raise AgentLimitError("Repeated tool call")
            seen.add(signature); calls += 1
            if calls > self.config.max_tool_calls: raise AgentLimitError("Maximum tool calls exceeded")
            result = self.registry.execute(request); messages.append({"role": "assistant", "content": json.dumps(decision)}); messages.append({"role": "user", "content": f"Tool result from {request.name}: {result.model_dump_json()}"})
            record(AgentEvent(type="tool", detail=request.name, step=step))
        raise AgentLimitError("Maximum agent steps exceeded")
