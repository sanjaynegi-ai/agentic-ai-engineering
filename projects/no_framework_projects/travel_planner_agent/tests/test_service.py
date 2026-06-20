import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pytest
from travel_planner_agent.service import run
def test_itinerary():
    result = run("Plan a 2-day Jaipur trip for 4 people")
    assert result.city == "Jaipur" and len(result.days) == 2 and result.sources
def test_requires_city():
    with pytest.raises(ValueError): run("Plan something")
