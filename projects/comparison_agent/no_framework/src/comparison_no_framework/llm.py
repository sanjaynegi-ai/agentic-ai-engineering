import json, os
from pathlib import Path
from openai import OpenAI
class OpenAILLM:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL") or None)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    def decide(self, messages: list[dict[str, str]]) -> dict:
        prompt = Path(__file__).resolve().parents[2] / "prompts" / "tool_selection.md"
        response = self.client.responses.create(model=self.model, instructions=prompt.read_text(encoding="utf-8"), input=messages, max_output_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", "1200")))
        return json.loads(response.output_text)
class ScriptedLLM:
    def __init__(self, decisions: list[dict]): self.decisions = iter(decisions)
    def decide(self, messages: list[dict[str, str]]) -> dict: return next(self.decisions)
