import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from customer_support_router.service import Route, run


def test_golden_routes():
    cases = json.loads((HERE / "data/eval_tickets.json").read_text(encoding="utf-8"))
    for case in cases:
        result = run(case["text"])
        assert result.route == case["route"]
        assert result.draft_response.startswith("Draft:")


def test_risk_escalates():
    assert run("I will file a chargeback for fraud").route == Route.HUMAN_REVIEW
