from collections import defaultdict
from datetime import datetime
from typing import Iterable

from pydantic import BaseModel, ValidationInfo, field_validator

from src.common.logger import logger
from src.common.utils.objects import chunks
from src.infras.aws import CloudwatchLogService, ECSService, LambdaService


# Models ------------------------------------
class CwQueryParam(BaseModel):
    log_group_names: Iterable[str]
    query_string: str
    start_time: datetime
    end_time: datetime
    timeout: int = 15
    delay: int = 1
    chunk_size: int = 10

    @field_validator("query_string", mode="after")
    @classmethod
    def validate_query_string(cls, value: str, info) -> str:
        if not value:
            raise ValueError("Query string cannot be empty")
        if not value.startswith("fields"):
            raise ValueError("Invalid query string format")
        if "@log" not in value or "@message" not in value:
            raise ValueError("Query string must include '@log' and '@message' fields")
        return value

    @field_validator("end_time", mode="after")
    @classmethod
    def validate_end_time(cls, value: datetime, info: ValidationInfo) -> datetime:
        if value < info.data.get("start_time"):
            raise ValueError("End time must be greater than or equal to start time")
        return value


class CwLog(BaseModel):
    timestamp: int | None = None
    message: str
    log: str
    log_stream: str | None = None


class CwQueryResult(BaseModel):
    log_group_name: str
    logs: list[CwLog] = []


# Service -----------------------------------
class CloudwatchService:
    def __init__(
        self,
        cloudwatch_log_service: CloudwatchLogService,
        lambda_service: LambdaService,
        ecs_service: ECSService,
    ):
        self.cloudwatch_log_service = cloudwatch_log_service
        self.lambda_service = lambda_service
        self.ecs_service = ecs_service

    def list_monitoring_log_groups(self) -> Iterable[str]:
        """List lambda function's log groups and ECS clusters' log groups that have monitoring enabled."""
        for function in self.lambda_service.list_functions():
            if function.get("Tags").get("monitoring", "").lower() == "true":
                if log_group := function.get("LoggingConfig", {}).get("LogGroup"):
                    yield log_group

        for cluster in self.ecs_service.list_clusters():
            if (
                log_group := cluster.get("configuration", {})
                .get("executeCommandConfiguration", {})
                .get("logConfiguration", {})
                .get("cloudWatchLogGroupName")
            ):
                yield log_group

    def query_error_logs(self, param: CwQueryParam) -> Iterable[CwQueryResult]:
        """Query logs from CloudWatch Logs using the provided parameters."""
        start_time = int(param.start_time.timestamp())
        end_time = int(param.end_time.timestamp())

        for chunk in chunks(param.log_group_names, param.chunk_size):
            logger.debug(f"Querying log groups: {chunk}")
            results = self.cloudwatch_log_service.query_logs(
                log_group_names=chunk,
                query_string=param.query_string,
                start_time=start_time,
                end_time=end_time,
                timeout=param.timeout,
                delay=param.delay,
            )
            logger.debug(f"Found {len(results)} logs matching the query")

            # categorize results by log_group_name
            categorized_results = defaultdict(list)
            for result in results:
                cw_log = CwLog.model_validate({item.get("field", " ")[1:]: item.get("value") for item in result})
                categorized_results[cw_log.log].append(cw_log)

            yield from (CwQueryResult(log_group_name=name, logs=logs) for name, logs in categorized_results.items())
