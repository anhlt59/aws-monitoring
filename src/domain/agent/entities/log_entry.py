from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from ..value_objects.log_level import LogLevel


class LogEntry(BaseModel):
    """Domain entity representing a log entry from monitoring"""

    timestamp: datetime = Field(..., description="Log entry timestamp")
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., min_length=1, description="Log message")
    source: str = Field(..., min_length=1, description="Log source")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    log_group: Optional[str] = Field(default=None, description="CloudWatch log group")
    log_stream: Optional[str] = Field(default=None, description="CloudWatch log stream")

    @field_validator("message", "source")
    @classmethod
    def validate_required_fields(cls, v: str) -> str:
        """Validate required string fields are not empty"""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    def is_error(self) -> bool:
        """Check if log entry represents an error"""
        return self.level.is_error_level()

    def contains_keyword(self, keyword: str) -> bool:
        """Check if log message contains specific keyword"""
        return keyword.lower() in self.message.lower()

    def has_metadata_key(self, key: str) -> bool:
        """Check if log entry has specific metadata key"""
        return key in self.metadata

    def get_metadata_value(self, key: str) -> Any:
        """Get metadata value by key"""
        return self.metadata.get(key)

    @classmethod
    def from_cloudwatch_log(
        cls,
        timestamp: datetime,
        message: str,
        log_group: str,
        log_stream: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "LogEntry":
        """Factory method to create log entry from CloudWatch log"""
        # Auto-detect log level from message
        level = cls._detect_log_level(message)

        return cls(
            timestamp=timestamp,
            level=level,
            message=message,
            source="cloudwatch",
            metadata=metadata or {},
            log_group=log_group,
            log_stream=log_stream,
        )

    @staticmethod
    def _detect_log_level(message: str) -> LogLevel:
        """Auto-detect log level from message content"""
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in ["critical", "fatal"]):
            return LogLevel.CRITICAL
        elif any(keyword in message_lower for keyword in ["error", "exception", "failed"]):
            return LogLevel.ERROR
        elif any(keyword in message_lower for keyword in ["warning", "warn"]):
            return LogLevel.WARNING
        elif any(keyword in message_lower for keyword in ["debug"]):
            return LogLevel.DEBUG
        else:
            return LogLevel.INFO
