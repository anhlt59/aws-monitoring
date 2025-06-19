from enum import Enum

from pydantic import BaseModel, Field
from uuid_utils import uuid7

from src.common.utils.datetime_utils import current_utc_timestamp


class Status(Enum, int):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4
    UNKNOWN = 5


# Model
class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid7()))
    project: str
    source: str
    detail: dict
    assigned: str | None = None
    status: Status = Status.PENDING
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)
