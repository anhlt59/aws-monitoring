from collections import defaultdict
from datetime import datetime
from typing import Iterable

from src.adapters.aws import CloudwatchLogService, ECSService, LambdaService
from src.common.logger import logger
from src.common.utils.objects import chunks
from src.domain.models.logs import LogEntry, LogQueryResult


# Service -----------------------------------
class LogService:
    def __init__(
        self,
        cloudwatch_log_service: CloudwatchLogService,
        lambda_service: LambdaService,
        ecs_service: ECSService,
    ):
        self.cloudwatch_log_service = cloudwatch_log_service
        self.lambda_service = lambda_service
        self.ecs_service = ecs_service

    def list_monitoring_log_groups_by_tag(self, tag_name: str, tag_value) -> Iterable[str]:
        """List lambda function's log groups and ECS clusters' log groups."""
        for function in self.lambda_service.list_functions():
            if function.get("Tags", {}).get(tag_name, "") == tag_value:
                yield function.get("LoggingConfig", {}).get("LogGroup")

        for cluster in self.ecs_service.list_clusters():
            if any((tag["key"], tag["value"]) == (tag_name, tag_value) for tag in cluster.get("tags", [])):
                if (
                    log_group := cluster.get("configuration", {})
                    .get("executeCommandConfiguration", {})
                    .get("logConfiguration", {})
                    .get("cloudWatchLogGroupName")
                ):
                    yield log_group

    def query_logs(
        self,
        log_group_names: list[str],
        query_string: str,
        start_time: datetime,
        end_time: datetime,
        timeout: int = 15,
        delay: int = 1,
        chunk_size: int = 10,
    ) -> Iterable[LogQueryResult]:
        """Query logs from CloudWatch Logs using the provided parameters.

        Maps CloudWatch query results to domain LogQueryResult model.
        """
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

            # categorize results by log_group_name and map to domain models
            categorized_results = defaultdict(list)
            for result in results:
                log_entry = LogEntry.model_validate({item.get("field", " ")[1:]: item.get("value") for item in result})
                categorized_results[log_entry.log].append(log_entry)

            yield from (LogQueryResult(log_group_name=name, logs=logs) for name, logs in categorized_results.items())
