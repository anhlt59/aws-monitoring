from pydantic import BaseModel


class LogEntry(BaseModel):
    timestamp: int | None = None
    message: str
    log: str
    log_stream: str | None = None


class LogQueryResult(BaseModel):
    log_group_name: str
    logs: list[LogEntry] = []
