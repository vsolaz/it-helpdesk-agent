"""Validation helpers for collected incident fields."""

REQUIRED_FIELDS: tuple[str, ...] = ("short_description", "description", "urgency", "category")


def validate_incident_fields(collected: dict) -> list[str]:
    """Return a list of field names that are still missing or blank.

    Args:
        collected: Dictionary of field names to their collected values.

    Returns:
        A (possibly empty) list of field names that need to be filled in.
        An empty list means all required fields are present and non-empty.
    """
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        value = collected.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(field)
    return missing
