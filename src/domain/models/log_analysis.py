from pydantic import BaseModel, Field, field_validator

from src.common.utils.datetime_utils import current_utc_timestamp

from .base import PaginatedInputDTO, QueryResult


# Model
class LogAnalysis(BaseModel):
    """Domain model for AI-powered log analysis results"""

    id: str  # Analysis hash for deduplication
    date: str  # YYYY-MM-DD format for daily grouping
    context_ids: list[str] = []  # Links to context schemas
    severity: int = 0  # 0=Unknown, 1=Low, 2=Medium, 3=High, 4=Critical
    categories: list[str] = []  # e.g., ["Database", "Connection", "Timeout"]
    patterns: list[str] = []  # Identified patterns
    frequency: int = 1  # Count of similar logs in the same day
    summary: str  # Concise summary
    solution: str | None = None  # Recommended solution
    log_sample: str  # Sample log entry
    event_ids: list[str] = []  # Links to related event IDs
    account: str  # AWS Account ID
    region: str | None = None  # AWS Region
    analyzed_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: int) -> int:
        if not 0 <= value <= 4:
            raise ValueError("Severity must be between 0 and 4")
        return value

    @property
    def persistence_id(self) -> str:
        return f"{self.date}#{self.id}"


# DTOs
class ListLogAnalysesDTO(PaginatedInputDTO):
    date: str | None = None  # Filter by specific date
    start_date: str | None = None  # Filter by date range
    end_date: str | None = None
    account: str | None = None
    severity_min: int | None = None  # Filter by minimum severity


class CreateLogAnalysisDTO(BaseModel):
    """DTO for creating a new log analysis"""

    date: str
    context_ids: list[str] = []
    severity: int
    categories: list[str]
    patterns: list[str]
    frequency: int = 1
    summary: str
    solution: str | None = None
    log_sample: str
    event_ids: list[str] = []
    account: str
    region: str | None = None


# Query Results
LogAnalysisQueryResult = QueryResult[LogAnalysis]
