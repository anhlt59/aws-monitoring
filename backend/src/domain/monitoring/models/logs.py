from pydantic import BaseModel, field_validator, ValidationInfo
from datetime import datetime


class LogEntry(BaseModel):
    timestamp: int | None = None
    message: str
    log: str
    log_stream: str | None = None


class LogQueryResult(BaseModel):
    log_group_name: str
    logs: list[LogEntry] = []


class LogQuery(BaseModel):
    query_string: str
    start_time: datetime
    end_time: datetime
    timeout: int = 15
    delay: int = 1
    chunk_size: int = 10
    filter_tag: dict = {"key": "monitoring", "value": "true"}

    @field_validator("query_string", mode="after")
    @classmethod
    def validate_query_string(cls, value: str, info) -> str:
        if not value:
            raise ValueError("Query string cannot be empty")
        if "@log" not in value or "@message" not in value:
            raise ValueError("Query string must include '@log' and '@message' fields")
        return value

    @field_validator("end_time", mode="after")
    @classmethod
    def validate_end_time(cls, value: datetime, info: ValidationInfo) -> datetime:
        if value < info.data.get("start_time"):
            raise ValueError("End time must be greater than or equal to start time")
        return value
