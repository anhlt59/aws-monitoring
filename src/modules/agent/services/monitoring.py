from collections import defaultdict
from datetime import datetime
from typing import Iterable

from pydantic import BaseModel, ValidationInfo, field_validator

from src.common.logger import logger
from src.common.utils.objects import chunks
from src.infras.aws import CloudwatchLogService, ECSService, EventBridgeService, LambdaService
from src.modules.agent.models import Event

MONITORING_TAG_NAME = "monitoring"
MONITORING_TAG_VALUE = "true"


# Models ------------------------------------
class QueryParam(BaseModel):
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
class MonitoringService:
    def __init__(
        self,
        cloudwatch_log_service: CloudwatchLogService,
        lambda_service: LambdaService,
        ecs_service: ECSService,
        publisher: EventBridgeService,
    ):
        self.cloudwatch_log_service = cloudwatch_log_service
        self.lambda_service = lambda_service
        self.ecs_service = ecs_service
        self.publisher = publisher

    def monitor_logs(self, param: QueryParam):
        """Query error logs use-case.
        1. List out all log groups that have monitoring enabled (by tag).
        2. Query logs from CloudWatch Logs using the provided parameters.
        3. Publish the results to the message broker.
        """
        # 1. list out all monitoring log groups
        log_groups = self._list_monitoring_log_groups_by_tag()

        # 2. query error logs from CloudWatch Logs
        error_logs = self._query_error_logs(
            log_groups,
            query_string=param.query_string,
            start_time=param.start_time,
            end_time=param.end_time,
            timeout=param.timeout,
            delay=param.delay,
            chunk_size=param.chunk_size,
        )

        # 3. publish the results to the message broker
        # convert error logs to a list of events
        events = [
            Event(
                source="monitoring.agent.logs",
                detail=log_result.model_dump_json(),
                detail_type="Error Log Query",
            )
            for log_result in error_logs
        ]
        # publish events if any
        if events:
            self._publish_events(events)

    def _list_monitoring_log_groups_by_tag(
        self,
        tag_name=MONITORING_TAG_NAME,
        tag_value=MONITORING_TAG_VALUE,
    ) -> Iterable[str]:
        """List lambda function's log groups and ECS clusters' log groups that have monitoring enabled."""
        for function in self.lambda_service.list_functions():
            if function.get("Tags").get(tag_name, "").lower() == tag_value:
                if log_group := function.get("LoggingConfig", {}).get("LogGroup"):
                    yield log_group

        for cluster in self.ecs_service.list_clusters():
            for tag in cluster.get("tags", []):
                if tag.get("key") == tag_name and tag.get("value", "").lower() == tag_value:
                    if (
                        log_group := cluster.get("configuration", {})
                        .get("executeCommandConfiguration", {})
                        .get("logConfiguration", {})
                        .get("cloudWatchLogGroupName")
                    ):
                        yield log_group

    def _query_error_logs(
        self,
        log_group_names: Iterable[str],
        query_string: str,
        start_time: datetime,
        end_time: datetime,
        timeout: int = 15,
        delay: int = 1,
        chunk_size: int = 10,
    ) -> Iterable[CwQueryResult]:
        """Query logs from CloudWatch Logs using the provided parameters."""
        for chunk in chunks(log_group_names, chunk_size):
            logger.debug(f"Querying log groups: {chunk}")
            results = self.cloudwatch_log_service.query_logs(
                log_group_names=chunk,
                query_string=query_string,
                start_time=int(start_time.timestamp()),
                end_time=int(end_time.timestamp()),
                timeout=timeout,
                delay=delay,
            )
            logger.debug(f"Found {len(results)} logs matching the query")

            # categorize results by log_group_name
            categorized_results = defaultdict(list)
            for result in results:
                cw_log = CwLog.model_validate({item.get("field", " ")[1:]: item.get("value") for item in result})
                categorized_results[cw_log.log].append(cw_log)

            yield from (CwQueryResult(log_group_name=name, logs=logs) for name, logs in categorized_results.items())

    def _publish_events(self, events: list[Event]):
        """Publish events to the message broker."""
        entries = [
            {
                "Source": event.source,
                "DetailType": event.detail_type,
                "Detail": event.detail,
                "Resources": event.resources,
                "Time": event.time,
            }
            for event in events
        ]
        if entries:
            logger.debug(f"Publishing {len(events)} error log events to EventBridge")
            self.publisher.put_events(entries)
