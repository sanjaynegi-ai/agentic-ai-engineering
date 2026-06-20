from comparison_openai_agents.agents import build_agents
def test_agent_construction():
    agents=build_agents(); assert {'triage','travel','budget','safety'} == set(agents)
