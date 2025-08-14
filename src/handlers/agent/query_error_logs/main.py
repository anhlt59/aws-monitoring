import os
from datetime import UTC, datetime, timedelta
from typing import Iterable

from src.adapters.aws.cloudwatch import CloudwatchLogService, CwQueryParam
from src.adapters.aws.ecs import ECSService
from src.adapters.aws.eventbridge import Event, EventBridgeService
from src.adapters.aws.lambda_function import LambdaService
from src.common.logger import logger
from src.common.utils.datetime_utils import round_n_minutes
from src.common.utils.objects import chunks

CW_INSIGHTS_QUERY_STRING = os.getenv(
    "CW_INSIGHTS_QUERY_STRING",
    "fields @message, @log, @logStream | filter @message like /(?i)(error|fail|exception)/ | sort @timestamp desc | limit 200",
)
CW_INSIGHTS_QUERY_DURATION = int(os.getenv("CW_INSIGHTS_QUERY_DURATION", 300))  # seconds
CW_INSIGHTS_QUERY_DELAY = int(os.getenv("CW_INSIGHTS_QUERY_DELAY", 1))  # seconds
CW_INSIGHTS_QUERY_TIMEOUT = int(os.getenv("CW_INSIGHTS_QUERY_TIMEOUT", 15))  # seconds
CW_LOGS_DELIVERY_LATENCY = int(os.getenv("CW_LOGS_DELIVERY_LATENCY", 15))  # seconds

cloudwatch_service = CloudwatchLogService()
publisher = EventBridgeService()
lambda_service = LambdaService()
ecs_service = ECSService()


def list_monitoring_log_groups() -> Iterable[str]:
    functions = lambda_service.list_monitoring_functions()
    clusters = ecs_service.list_monitoring_clusters()

    for function in functions:
        if log_group := function.get("LoggingConfig", {}).get("LogGroup"):
            yield log_group

    for cluster in clusters:
        if (
            log_group := cluster.get("configuration", {})
            .get("executeCommandConfiguration", {})
            .get("logConfiguration", {})
            .get("cloudWatchLogGroupName")
        ):
            yield log_group


# @logger.inject_lambda_context(log_event=True)
def handler(event, context):
    """Handle the incoming event."""
    end_time = round_n_minutes(datetime.now(UTC), 5) - timedelta(seconds=CW_LOGS_DELIVERY_LATENCY)
    start_time = end_time - timedelta(seconds=CW_INSIGHTS_QUERY_DURATION)

    # list out monitoring log groups
    log_groups = ["/aws/lambda/cmplus-testing"]  # list_monitoring_log_groups()

    for chunk in chunks(log_groups, 10):
        logger.debug(f"Querying log groups: {chunk}")
        results = cloudwatch_service.query_logs(
            CwQueryParam(
                log_group_names=chunk,
                query_string=CW_INSIGHTS_QUERY_STRING,
                end_time=int(end_time.timestamp()),
                start_time=int(start_time.timestamp()),
                timeout=CW_INSIGHTS_QUERY_TIMEOUT,
                delay=CW_INSIGHTS_QUERY_DELAY,
            )
        )
        logger.debug(f"Found {len(results)} logs matching the query")

        for log_result in results:
            event = Event(
                source="monitoring.agent",
                detail_type="Query Error Logs",
                detail=log_result.model_dump_json(),
            )
            publisher.publish(event)
