import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pytest
from comparison_no_framework.errors import UnknownToolError
from comparison_no_framework.schemas import ToolCallRequest
from comparison_no_framework.tool_registry import ToolRegistry
def test_unknown_tool():
    with pytest.raises(UnknownToolError): ToolRegistry().execute(ToolCallRequest(name='missing'))
