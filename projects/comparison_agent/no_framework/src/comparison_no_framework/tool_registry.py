from collections.abc import Callable
from typing import Any
from .errors import UnknownToolError
from .schemas import ToolCallRequest, ToolCallResult
from .tools import calculate, get_current_time, get_weather, search_local_notes
class ToolRegistry:
    def __init__(self, tools: dict[str, Callable[..., Any]] | None = None):
        self.tools = tools or {"calculate": calculate, "get_current_time": get_current_time, "get_weather": get_weather, "search_local_notes": search_local_notes}
    def execute(self, request: ToolCallRequest) -> ToolCallResult:
        if request.name not in self.tools: raise UnknownToolError(request.name)
        try: output = self.tools[request.name](**request.arguments); return ToolCallResult(name=request.name, ok=True, output=output.model_dump(mode="json") if hasattr(output, "model_dump") else output)
        except Exception as exc: return ToolCallResult(name=request.name, ok=False, output=str(exc))
