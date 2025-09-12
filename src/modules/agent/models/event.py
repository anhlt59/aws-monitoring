from datetime import UTC, datetime

from pydantic import BaseModel, Field


# Model
class Event(BaseModel):
    source: str
    detail_type: str
    detail: str
    resources: list[str] = []
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))
