import pytest
from pydantic import ValidationError
from comparison_openai_agents.schemas import TravelItinerary
def test_travelers_positive():
    with pytest.raises(ValidationError): TravelItinerary(city='Jaipur',travelers=0,days=[],estimated_budget_inr=0,umbrella_advice='check')
