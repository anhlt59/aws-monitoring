from enum import Enum

from pydantic import BaseModel, Field, model_validator

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
    id: str
    account: str
    source: str
    detail: dict
    assigned: str | None = None
    status: Status = Status.PENDING
    published_at: int = Field(default_factory=current_utc_timestamp)


# DTOs
class UpdateEventDTO(BaseModel):
    assigned: str | None = None
    status: Status | None = None
    updated_at: int = Field(default_factory=current_utc_timestamp)

    @model_validator(mode="after")
    def validate_model(self):
        if self.status is None and self.assigned is None:
            raise ValueError("At least one of 'status' or 'assigned' must be provided.")
        return self


class ListEventsDTO(BaseModel):
    start_date: int | None = None
    end_date: int | None = None
    limit: int = 50
    direction: str = "desc"
    cursor: dict | None = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date.")
        return self
