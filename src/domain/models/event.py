from pydantic import BaseModel, Field, model_validator

from src.common.utils.datetime_utils import current_utc_timestamp

from .base import PaginatedInputDTO, QueryResult


# Model
class Event(BaseModel):
    id: str  # AWS EventID
    account: str
    region: str | None = None
    source: str
    detail: dict
    detail_type: str | None = None
    resources: list[str] = []
    analysis_id: str | None = None  # Link to AI log analysis result
    published_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)

    @property
    def persistence_id(self) -> str:
        return f"{self.published_at}-{self.id}"


# DTOs
class ListEventsDTO(PaginatedInputDTO):
    start_date: int | None = None
    end_date: int | None = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date.")
        return self


# Query Results
EventQueryResult = QueryResult[Event]
