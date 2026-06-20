import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from comparison_no_framework.schemas import AgentConfig
import pytest
from pydantic import ValidationError
def test_config_rejects_zero_steps():
    with pytest.raises(ValidationError): AgentConfig(max_steps=0)
