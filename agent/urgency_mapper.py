from agent.models import Urgency

HIGH_KEYWORDS: frozenset[str] = frozenset({"urgent", "critical", "asap", "high"})
MEDIUM_KEYWORDS: frozenset[str] = frozenset({"medium", "normal", "moderate"})
LOW_KEYWORDS: frozenset[str] = frozenset({"low", "not urgent", "whenever"})

def map_urgency(text: str) -> Urgency:
    normalised = text.lower().strip()
    for kw in HIGH_KEYWORDS:
        if kw in normalised: return Urgency.HIGH
    for kw in MEDIUM_KEYWORDS:
        if kw in normalised: return Urgency.MEDIUM
    for kw in LOW_KEYWORDS:
        if kw in normalised: return Urgency.LOW
    return Urgency.MEDIUM
