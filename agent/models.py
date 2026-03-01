from dataclasses import dataclass
from typing import Optional
from enum import IntEnum

class Urgency(IntEnum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class IncidentFields:
    short_description: str
    description: str
    urgency: Urgency
    category: str

@dataclass
class ConversationState:
    session_id: str
    history: list[dict]
    collected: dict
    stage: str
    last_active: float

@dataclass
class IncidentResult:
    success: bool
    ticket_number: Optional[str]
    error_message: Optional[str]
