import importlib.util
from pathlib import Path

import pytest

SERVICE = Path(__file__).resolve().parents[1] / "src/research_assistant_agent/service.py"
SPEC = importlib.util.spec_from_file_location("sdk_research_assistant_service", SERVICE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_agent, run = MODULE.build_agent, MODULE.run


def test_agent_and_grounded_offline_contract():
    result = run("What do guardrails constrain?")
    assert build_agent().name == "Research Assistant Agent"
    assert result.grounded is True
    assert result.citations


def test_unknown_topic_reports_insufficient_evidence():
    result = run("Explain photosynthesis")
    assert result.grounded is False
    assert result.citations == []


def test_empty():
    with pytest.raises(ValueError):
        run("")
