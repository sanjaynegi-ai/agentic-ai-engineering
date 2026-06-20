import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pytest
from comparison_no_framework.agent import TravelAgent
from comparison_no_framework.errors import AgentLimitError
from comparison_no_framework.llm import ScriptedLLM
from comparison_no_framework.schemas import AgentConfig
def test_final():
    result=TravelAgent(ScriptedLLM([{'type':'final','final':{'answer':'Jaipur itinerary'}}])).run('Plan a Jaipur trip')
    assert 'Jaipur' in result.answer
def test_max_steps():
    agent=TravelAgent(ScriptedLLM([{'type':'tool','tool':{'name':'get_current_time','arguments':{}}}]), AgentConfig(max_steps=1,max_tool_calls=2))
    with pytest.raises(AgentLimitError): agent.run('Plan a Jaipur trip')
