import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
PROMPTS = Path(__file__).resolve().parents[2] / "prompts"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "4000"))
def prompt(name: str) -> str: return (PROMPTS / name).read_text(encoding="utf-8")
