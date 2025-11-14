from datetime import datetime

from pydantic import BaseModel, ValidationInfo, field_validator

from src.common.utils.objects import chunks
from src.domain.models.messages import Message
from src.domain.ports.logs import ILogService
from src.domain.ports.publisher import IPublisher


class QueryParam(BaseModel):
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


async def query_error_logs_use_case(query: QueryParam, log_service: ILogService, publisher: IPublisher):
    """Query error logs use-case.
    1. List out all log groups that have monitoring enabled (by tag).
    2. Query logs from CloudWatch Logs using the provided parameters.
    3. Publish the results to the message broker.
    """
    # 1. list out all monitoring log groups
    log_groups = []
    async for log_group in log_service.list_monitoring_log_groups_by_tag(query.filter_tag["key"], query.filter_tag["value"]):
        log_groups.append(log_group)

    for chunk in chunks(log_groups, query.chunk_size):
        # 2. query error logs from CloudWatch Logs
        messages = []
        async for log_result in log_service.query_logs(
            chunk,
            query_string=query.query_string,
            start_time=query.start_time,
            end_time=query.end_time,
            timeout=query.timeout,
            delay=query.delay,
        ):
            messages.append(
                Message(
                    source="monitoring.agent.logs",
                    detail_type="Error Log Query",
                    detail=log_result.model_dump_json(),
                    resources=[log_result.log_group_name],
                )
            )

        # 3. publish the results to the message broker
        if messages:
            await publisher.publish(messages)
