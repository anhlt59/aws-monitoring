import re

from pydantic import BaseModel, Field, field_validator, model_validator

from src.common.utils.datetime_utils import current_utc_timestamp

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
        if not value.isdigit() or len(value) != 12:
            raise ValueError("Account must be exactly 12 digits")
        return value

    @field_validator("region")
    @classmethod
    def validate_region(cls, value: str) -> str:
        if not re.match(r"^[a-z]{2}-[a-z]+-\d{1}$", value):
            raise ValueError("Invalid AWS region format")
        return value

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        if not value.startswith("aws.") and not value.startswith("monitoring."):
            raise ValueError("Source must start with 'aws.' or 'monitoring.' prefix")
        return value

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: int) -> int:
        if not 0 <= value <= 5:
            raise ValueError("Severity must be between 0 and 5")
        return value

    @model_validator(mode="after")
    def set_expired_at(self):
        if not self.expired_at or self.expired_at < self.published_at:
            self.expired_at = self.published_at + (DEFAULT_TTL_DAYS * SECONDS_PER_DAY)
        return self

    def is_critical(self) -> bool:
        return self.severity >= 4

    def is_high_priority(self) -> bool:
        return self.severity >= 3

    def get_severity_label(self) -> str:
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
        current_time = current_utc_timestamp()
        seconds_remaining = self.expired_at - current_time
        return max(0, seconds_remaining // SECONDS_PER_DAY)
