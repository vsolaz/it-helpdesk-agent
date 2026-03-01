REQUIRED_FIELDS: tuple[str, ...] = ("short_description", "description", "urgency", "category")

def validate_incident_fields(collected: dict) -> list[str]:
    missing = []
    for field in REQUIRED_FIELDS:
        value = collected.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(field)
    return missing
