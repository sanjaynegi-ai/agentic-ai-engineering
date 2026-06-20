import importlib.util
from pathlib import Path

import pytest

SERVICE = Path(__file__).resolve().parents[1] / "src/customer_support_router/service.py"
SPEC = importlib.util.spec_from_file_location("sdk_customer_support_service", SERVICE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
Route, build_agent, run = MODULE.Route, MODULE.build_agent, MODULE.run


def test_agent_and_offline_contract():
    result = run("I was charged twice")
    assert build_agent().name == "Customer Support Router"
    assert result.route == Route.BILLING
    assert result.escalate is False
    assert result.draft_response.startswith("Draft:")


def test_risky_ticket_escalates():
    result = run("This may involve fraud")
    assert result.route == Route.HUMAN_REVIEW
    assert result.escalate is True


def test_empty():
    with pytest.raises(ValueError):
        run("")
