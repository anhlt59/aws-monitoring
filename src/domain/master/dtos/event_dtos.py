from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from ...common import PaginatedRequest
from ..value_objects.severity import Severity


class CreateEventDTO(BaseModel):
    """DTO for creating a new monitoring event"""

    id: str = Field(..., min_length=1, description="Event ID")
    account: str = Field(..., min_length=1, description="AWS Account ID")
    region: str = Field(..., min_length=1, description="AWS Region")
    source: str = Field(..., min_length=1, description="Event source")
    detail: dict = Field(..., description="Event detail payload")
    detail_type: str = Field(..., min_length=1, description="Event detail type")
    severity: Optional[Severity] = Field(default=None, description="Event severity level")
    resources: list[str] = Field(default_factory=list, description="Associated resource ARNs")
    published_at: Optional[datetime] = Field(default=None, description="Event publication timestamp")


class ListEventsDTO(PaginatedRequest):
    """DTO for listing events with filtering"""

    start_date: Optional[datetime] = Field(default=None, description="Start date filter")
    end_date: Optional[datetime] = Field(default=None, description="End date filter")
    account: Optional[str] = Field(default=None, description="Filter by account")
    severity: Optional[Severity] = Field(default=None, description="Filter by severity")
    source: Optional[str] = Field(default=None, description="Filter by source")

    @model_validator(mode="after")
    def validate_date_range(self):
        """Validate date range"""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
        return self


class EventSummaryDTO(BaseModel):
    """DTO for event summary"""

    total_events: int = Field(..., description="Total number of events")
    critical_events: int = Field(..., description="Number of critical events")
    high_events: int = Field(..., description="Number of high severity events")
    medium_events: int = Field(..., description="Number of medium severity events")
    low_events: int = Field(..., description="Number of low severity events")
    unknown_events: int = Field(..., description="Number of unknown severity events")
    time_range: dict = Field(..., description="Time range of the summary")
