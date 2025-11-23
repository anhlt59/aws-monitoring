from pydantic import BaseModel, Field, field_validator, model_validator

from src.common.utils.datetime_utils import current_utc_timestamp

from .base import PaginatedInputDTO, QueryResult

# 90 days in seconds
DEFAULT_TTL_DAYS = 90
SECONDS_PER_DAY = 86400


# Model
class Event(BaseModel):
    id: str  # PublishedAt + EventUUID
    account: str
    region: str
    source: str
    detail_type: str
    detail: dict
    severity: int = 0  # Severity level (0-5, where 5 is most severe)
    resources: list[str] = []
    published_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)
    expired_at: int = Field(default_factory=lambda: current_utc_timestamp() + (DEFAULT_TTL_DAYS * SECONDS_PER_DAY))

    @field_validator("account")
    @classmethod
    def validate_account(cls, value: str) -> str:
        """Validate AWS account ID format."""
        if not value.isdigit() or len(value) != 12:
            raise ValueError("Account must be exactly 12 digits")
        return value

    @field_validator("region")
    @classmethod
    def validate_region(cls, value: str) -> str:
        """Validate AWS region format."""
        import re

        if not re.match(r"^[a-z]{2}-[a-z]+-\d{1}$", value):
            raise ValueError("Invalid AWS region format")
        return value

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        """Validate event source format."""
        if not value.startswith("aws.") and not value.startswith("monitoring."):
            raise ValueError("Source must start with 'aws.' or 'monitoring.' prefix")
        return value

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: int) -> int:
        """Validate severity level."""
        if not 0 <= value <= 5:
            raise ValueError("Severity must be between 0 and 5")
        return value

    @model_validator(mode="after")
    def set_expired_at(self):
        """Ensure expired_at is set based on published_at if not provided."""
        if self.expired_at == 0 or self.expired_at < self.published_at:
            self.expired_at = self.published_at + (DEFAULT_TTL_DAYS * SECONDS_PER_DAY)
        return self

    def is_critical(self) -> bool:
        """Check if event is critical (severity >= 4)."""
        return self.severity >= 4

    def is_high_priority(self) -> bool:
        """Check if event is high priority (severity >= 3)."""
        return self.severity >= 3

    def get_severity_label(self) -> str:
        """Get severity label for display."""
        severity_labels = {
            0: "info",
            1: "low",
            2: "medium",
            3: "high",
            4: "critical",
            5: "emergency",
        }
        return severity_labels.get(self.severity, "unknown")

    def days_until_expiry(self) -> int:
        """Calculate days until event expiration."""
        current_time = current_utc_timestamp()
        seconds_remaining = self.expired_at - current_time
        return max(0, seconds_remaining // SECONDS_PER_DAY)


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
