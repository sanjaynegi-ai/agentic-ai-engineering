import os
from enum import StrEnum

from agents import Agent, Runner
from pydantic import BaseModel, Field


class Route(StrEnum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    SALES = "sales"
    HUMAN_REVIEW = "human_review"


class RoutingResult(BaseModel):
    route: Route
    confidence: float = Field(ge=0, le=1)
    reason: str
    escalate: bool
    draft_response: str


RULES = {
    Route.BILLING: {"charge", "refund", "invoice", "payment"},
    Route.TECHNICAL: {"error", "crash", "bug", "broken"},
    Route.ACCOUNT: {"login", "password", "account", "delete"},
    Route.SALES: {"price", "demo", "plan", "buy"},
}
RISK = {"fraud", "legal", "chargeback", "threat", "harassment", "personal data"}


def build_agent() -> Agent:
    return Agent(
        name="Customer Support Router",
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=(
            "Classify a support ticket, escalate ambiguous or risky requests, and create a draft "
            "response. Never send the response or modify an account."
        ),
        output_type=RoutingResult,
    )


def run(text: str) -> RoutingResult:
    """Deterministic offline path matching the no-framework routing rules."""
    clean = text.strip()
    lower = clean.lower()
    if not clean:
        raise ValueError("Input cannot be empty")
    if any(term in lower for term in RISK):
        return RoutingResult(
            route=Route.HUMAN_REVIEW,
            confidence=1,
            reason="Risk keyword requires human review",
            escalate=True,
            draft_response="Draft: A specialist must review this request before we respond.",
        )

    scores = {route: sum(term in lower for term in terms) for route, terms in RULES.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return RoutingResult(
            route=Route.HUMAN_REVIEW,
            confidence=0.25,
            reason="No reliable route",
            escalate=True,
            draft_response="Draft: We received your request and are routing it for review.",
        )

    tied = sum(score == scores[best] for score in scores.values()) > 1
    return RoutingResult(
        route=Route.HUMAN_REVIEW if tied else best,
        confidence=0.5 if tied else 0.9,
        reason="Matched deterministic routing terms",
        escalate=tied,
        draft_response="Draft: We received your request and will review it.",
    )


async def run_live(text: str) -> RoutingResult:
    result = await Runner.run(build_agent(), input=text, max_turns=8)
    return result.final_output
