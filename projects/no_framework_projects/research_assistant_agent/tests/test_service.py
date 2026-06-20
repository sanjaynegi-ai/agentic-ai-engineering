import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from research_assistant_agent.service import run
def test_grounded_answer():
    result=run("What do guardrails constrain?"); assert result.grounded and result.citations
def test_unknown_is_not_grounded(): assert run("quantum banana").grounded is False
