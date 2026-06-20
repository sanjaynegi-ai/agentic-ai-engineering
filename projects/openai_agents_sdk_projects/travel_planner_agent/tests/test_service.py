import importlib.util
from pathlib import Path

import pytest

SERVICE = Path(__file__).resolve().parents[1] / "src/travel_planner_agent/service.py"
SPEC = importlib.util.spec_from_file_location("sdk_travel_planner_service", SERVICE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_agent, run = MODULE.build_agent, MODULE.run


def test_agent_and_offline_contract():
    result = run("Plan a 2-day Jaipur trip for 4 people")
    assert build_agent().name == "Travel Planner Agent"
    assert result.city == "Jaipur"
    assert result.travelers == 4
    assert len(result.days) == 2
    assert result.sources


def test_requires_supported_city():
    with pytest.raises(ValueError, match="supported city"):
        run("Plan a two day trip")


def test_empty():
    with pytest.raises(ValueError):
        run("")
