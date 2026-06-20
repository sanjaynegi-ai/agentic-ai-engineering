import os
from pathlib import Path
from dotenv import load_dotenv
from .schemas import AgentConfig
load_dotenv()
ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "local_notes" / "travel_india.md"
PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"
def load_config() -> AgentConfig:
    return AgentConfig(max_steps=int(os.getenv("MAX_AGENT_STEPS", "8")), max_tool_calls=int(os.getenv("MAX_TOOL_CALLS", "10")), max_input_chars=int(os.getenv("MAX_INPUT_CHARS", "4000")))
