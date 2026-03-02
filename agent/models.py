"""Domain models for the IT Helpdesk Agent.

This module defines the core data structures shared across the agent pipeline:
incident field collection, conversation state, and submission results.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class Urgency(IntEnum):
    """ServiceNow urgency levels (lower value = higher urgency)."""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class IncidentFields:
    """Validated fields required to open a ServiceNow incident ticket."""

    short_description: str
    """One-line summary of the issue."""

    description: str
    """Detailed description of the issue."""

    urgency: Urgency
    """Urgency level of the incident."""

    category: str
    """Incident category (e.g. 'hardware', 'software', 'network')."""


@dataclass
class ConversationState:
    """Mutable state carried through the LangGraph conversation pipeline."""

    session_id: str
    """Unique identifier for this conversation session."""

    history: list[dict]
    """Ordered list of ``{"role": str, "content": str}`` message dicts."""

    collected: dict
    """Partially or fully collected incident field values."""

    stage: str
    """Current pipeline stage: 'collect' | 'confirm' | 'submit' | 'error' | 'done'."""

    last_active: float
    """Unix timestamp of the most recent state update (used for TTL)."""


@dataclass
class IncidentResult:
    """Outcome of a ServiceNow incident creation attempt."""

    success: bool
    """Whether the ticket was created successfully."""

    ticket_number: Optional[str]
    """The ServiceNow incident number, e.g. 'INC0012345' (None on failure)."""

    error_message: Optional[str]
    """Human-readable error description (None on success)."""
