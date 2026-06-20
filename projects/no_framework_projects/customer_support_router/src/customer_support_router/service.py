from enum import StrEnum
from pydantic import BaseModel, Field
class Route(StrEnum): BILLING="billing"; TECHNICAL="technical"; ACCOUNT="account"; SALES="sales"; HUMAN_REVIEW="human_review"
class RoutingResult(BaseModel):
    route: Route
    confidence: float = Field(ge=0, le=1)
    reason: str
    escalate: bool
    draft_response: str
RULES = {Route.BILLING:{"charge","refund","invoice","payment"},Route.TECHNICAL:{"error","crash","bug","broken"},Route.ACCOUNT:{"login","password","account","delete"},Route.SALES:{"price","demo","plan","buy"}}
RISK = {"fraud","legal","chargeback","threat","harassment","personal data"}
def run(text: str) -> RoutingResult:
    clean=text.strip(); lower=clean.lower()
    if not clean: raise ValueError("Input cannot be empty")
    if any(term in lower for term in RISK): return RoutingResult(route=Route.HUMAN_REVIEW,confidence=1,reason="Risk keyword requires human review",escalate=True,draft_response="Draft: A specialist must review this request before we respond.")
    scores={route:sum(term in lower for term in terms) for route,terms in RULES.items()}; best=max(scores,key=scores.get)
    if scores[best] == 0: return RoutingResult(route=Route.HUMAN_REVIEW,confidence=.25,reason="No reliable route",escalate=True,draft_response="Draft: We received your request and are routing it for review.")
    ties=sum(score==scores[best] for score in scores.values())>1
    return RoutingResult(route=Route.HUMAN_REVIEW if ties else best,confidence=.5 if ties else .9,reason="Matched deterministic routing terms",escalate=ties,draft_response="Draft: We received your request and will review it.")
