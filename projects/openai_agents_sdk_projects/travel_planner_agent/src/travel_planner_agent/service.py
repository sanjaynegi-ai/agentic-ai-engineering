from __future__ import annotations

import os
import re

from agents import Agent, Runner
from pydantic import BaseModel, Field


class Itinerary(BaseModel):
    city: str
    travelers: int
    days: list[str]
    estimated_budget_inr: int
    umbrella_advice: str
    sources: list[str] = Field(default_factory=list)


CITY_COSTS = {
    "jaipur": 5500,
    "goa": 7500,
    "delhi": 6500,
    "mumbai": 8000,
    "bengaluru": 7000,
}


def build_agent() -> Agent:
    return Agent(
        name="Travel Planner Agent",
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=(
            "Create a bounded travel plan. Coordinate itinerary, budget, and packing concerns; "
            "cite supplied local notes; never claim to make a booking."
        ),
        output_type=Itinerary,
    )


def run(text: str) -> Itinerary:
    """Deterministic offline path matching the no-framework project contract."""
    clean = text.strip()
    lower = clean.lower()
    if not clean:
        raise ValueError("Input cannot be empty")

    city = next((name.title() for name in CITY_COSTS if name in lower), None)
    if not city:
        raise ValueError("Mention one supported city: Jaipur, Goa, Delhi, Mumbai, or Bengaluru")

    travelers_match = re.search(r"(?:for|of)\s+(\d+)\s+(?:people|person|travelers|family)", lower)
    days_match = re.search(r"(\d+)\s*[- ]?day", lower)
    travelers = int(travelers_match.group(1)) if travelers_match else 2
    day_count = min(int(days_match.group(1)) if days_match else 2, 7)
    estimate = CITY_COSTS[city.lower()] * day_count + 1200 * travelers
    days = [
        f"Day {day}: grouped local sights, meal break, and weather fallback"
        for day in range(1, day_count + 1)
    ]
    return Itinerary(
        city=city,
        travelers=travelers,
        days=days,
        estimated_budget_inr=estimate,
        umbrella_advice=(
            "Check a current forecast; carry a compact umbrella when rain is possible."
        ),
        sources=["data/travel_india.md"],
    )


async def run_live(text: str) -> Itinerary:
    result = await Runner.run(build_agent(), input=text, max_turns=8)
    return result.final_output
