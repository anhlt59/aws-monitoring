from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..value_objects.log_level import LogLevel


class LogQueryDTO(BaseModel):
    """DTO for querying logs"""

    log_groups: list[str] = Field(..., min_items=1, description="Log groups to query")
    start_time: datetime = Field(..., description="Query start time")
    end_time: datetime = Field(..., description="Query end time")
    filter_pattern: Optional[str] = Field(default=None, description="CloudWatch filter pattern")
    log_level: Optional[LogLevel] = Field(default=None, description="Minimum log level to include")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of results")


class LogSummaryDTO(BaseModel):
    """DTO for log analysis summary"""

    total_logs: int = Field(..., description="Total number of logs")
    error_count: int = Field(..., description="Number of error logs")
    warning_count: int = Field(..., description="Number of warning logs")
    info_count: int = Field(..., description="Number of info logs")
    debug_count: int = Field(..., description="Number of debug logs")
    time_range: dict = Field(..., description="Time range of analysis")
    log_groups: list[str] = Field(..., description="Analyzed log groups")


class PublishLogEventDTO(BaseModel):
    """DTO for publishing log events to master"""

    account: str = Field(..., min_length=1, description="AWS Account ID")
    region: str = Field(..., min_length=1, description="AWS Region")
    log_group: str = Field(..., min_length=1, description="CloudWatch log group")
    log_stream: str = Field(..., min_length=1, description="CloudWatch log stream")
    timestamp: datetime = Field(..., description="Log timestamp")
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., min_length=1, description="Log message")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
