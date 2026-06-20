from __future__ import annotations

import os
from pathlib import Path

from agents import Agent, Runner
from pydantic import BaseModel, Field


class ResearchAnswer(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)
    grounded: bool


DATA = Path(__file__).resolve().parents[2] / "data" / "notes"


def build_agent() -> Agent:
    return Agent(
        name="Research Assistant Agent",
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=(
            "Answer only from the supplied local Markdown evidence. Include file citations and say "
            "when the evidence is insufficient."
        ),
        output_type=ResearchAnswer,
    )


def run(text: str) -> ResearchAnswer:
    """Deterministic offline retrieval matching the no-framework project contract."""
    clean = text.strip()
    if not clean:
        raise ValueError("Input cannot be empty")

    query = {word.lower().strip(".,?!") for word in clean.split() if len(word) > 3}
    ranked: list[tuple[int, Path, str]] = []
    for path in DATA.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        score = sum(word in content.lower() for word in query)
        if score:
            ranked.append((score, path, content))
    ranked.sort(reverse=True, key=lambda item: item[0])
    if not ranked:
        return ResearchAnswer(
            answer="I do not have enough evidence in the local notes.", grounded=False
        )
    return ResearchAnswer(
        answer=ranked[0][2].splitlines()[-1],
        citations=[f"{ranked[0][1].name}:1"],
        grounded=True,
    )


async def run_live(text: str) -> ResearchAnswer:
    result = await Runner.run(build_agent(), input=text, max_turns=8)
    return result.final_output
