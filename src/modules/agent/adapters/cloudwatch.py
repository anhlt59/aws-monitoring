from datetime import datetime
from typing import Iterable

from src.common.logger import logger
from src.common.utils.objects import chunks
from src.infras.aws import CloudwatchLogService, ECSService, LambdaService
from src.infras.aws.cloudwatch import CwQueryParam, CwQueryResult
from src.modules.agent.configs import CW_INSIGHTS_QUERY_TIMEOUT, CW_LOG_GROUPS_CHUNK_SIZE


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

    def query_error_logs(
        self,
        log_groups: Iterable[str],
        query_string: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Iterable[CwQueryResult]:
        """Query logs from CloudWatch Logs using the provided parameters."""
        for chunk in chunks(log_groups, CW_LOG_GROUPS_CHUNK_SIZE):
            logger.debug(f"Querying log groups: {chunk}")
            results = self.cloudwatch_log_service.query_logs(
                CwQueryParam(
                    log_group_names=chunk,
                    query_string=query_string,
                    end_time=int(end_time.timestamp()),
                    start_time=int(start_time.timestamp()),
                    timeout=CW_INSIGHTS_QUERY_TIMEOUT,
                )
            )
            logger.debug(f"Found {len(results)} logs matching the query")
            yield from results
