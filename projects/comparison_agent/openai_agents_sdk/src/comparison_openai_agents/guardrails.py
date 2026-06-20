from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, TResponseInputItem, input_guardrail
from .config import MAX_INPUT_CHARS
TRAVEL = {"travel", "trip", "itinerary", "jaipur", "delhi", "mumbai", "goa", "bengaluru", "weather", "budget", "hotel", "flight", "train"}
def check_text(text: str) -> tuple[bool, str]:
    if len(text) > MAX_INPUT_CHARS: return False, "Input is too long"
    if not any(term in text.lower() for term in TRAVEL): return False, "Travel requests only"
    if any(term in text.lower() for term in ("evade security", "fake passport", "harm")): return False, "Unsafe travel advice is out of scope"
    return True, "ok"
@input_guardrail
async def travel_scope_guardrail(ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    text = input if isinstance(input, str) else str(input); ok, reason = check_text(text)
    return GuardrailFunctionOutput(output_info={"reason": reason}, tripwire_triggered=not ok)
