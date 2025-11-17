"""Domain models for log data.

These models represent log data structures in the domain layer,
independent of any specific log storage or querying implementation.
"""

from pydantic import BaseModel


class LogEntry(BaseModel):
    """Domain model for a single log entry.

    Attributes:
        timestamp: Unix timestamp of the log entry (milliseconds)
        message: Main log message content
        log: Log group name where this entry was found
        log_stream: Log stream name (optional)
    """

    timestamp: int | None = None
    message: str
    log: str
    log_stream: str | None = None


class LogQueryResult(BaseModel):
    """Domain model for log query results.

    Attributes:
        log_group_name: Name of the log group that was queried
        logs: List of log entries found in the query
    """

    log_group_name: str
    logs: list[LogEntry] = []
