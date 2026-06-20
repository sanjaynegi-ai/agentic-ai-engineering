from agents import Agent
from .config import MODEL, prompt
from .guardrails import travel_scope_guardrail
from .schemas import TravelItinerary
from .tools import calculate, get_current_time, get_weather, search_local_notes
def build_agents():
    budget = Agent(name="Budget specialist", model=MODEL, instructions=prompt("budget_agent.md"), tools=[calculate])
    safety = Agent(name="Safety and packing specialist", model=MODEL, instructions=prompt("safety_guardrail.md"), tools=[get_weather, get_current_time])
    travel = Agent(name="Travel planner", model=MODEL, instructions=prompt("travel_agent.md"), tools=[get_weather, search_local_notes, calculate], handoffs=[budget, safety], output_type=TravelItinerary)
    triage = Agent(name="Travel triage", model=MODEL, instructions=prompt("triage_agent.md"), handoffs=[travel, budget, safety], input_guardrails=[travel_scope_guardrail])
    return {"triage": triage, "travel": travel, "budget": budget, "safety": safety}
