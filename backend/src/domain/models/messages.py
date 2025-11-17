"""Domain models for event messages.

These models represent messages published to event systems,
independent of any specific messaging or event bus implementation.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Domain model for event messages published to event bus.

    Attributes:
        source: Source of the event (e.g., 'custom.monitoring')
        detail_type: Type of the event detail
        detail: JSON-serialized event detail payload
        resources: List of ARNs for resources related to the event
        time: Timestamp when the event was generated
    """

    source: str
    detail_type: str
    detail: str
    resources: list[str] = []
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))
