from .errors import GuardrailError
TRAVEL_TERMS = {"travel", "trip", "itinerary", "hotel", "weather", "jaipur", "delhi", "mumbai", "bengaluru", "goa", "budget", "flight", "train"}
def validate_input(text: str, max_chars: int = 4000) -> str:
    clean = text.strip()
    if not clean: raise GuardrailError("Input cannot be empty")
    if len(clean) > max_chars: raise GuardrailError(f"Input exceeds {max_chars} characters")
    if not any(term in clean.lower() for term in TRAVEL_TERMS): raise GuardrailError("This agent handles travel planning only")
    if any(term in clean.lower() for term in ("evade security", "fake passport", "harm")): raise GuardrailError("Unsafe travel advice is out of scope")
    return clean
def validate_output(text: str) -> str:
    if any(term in text.lower() for term in ("booking confirmed", "i booked", "guaranteed safe")): raise GuardrailError("Output makes a prohibited operational claim")
    return text
