from datetime import UTC, datetime, timedelta

from src.common.logger import logger
from src.common.utils.datetime_utils import round_n_minutes
from src.infras.aws import CloudwatchLogService, ECSService, EventBridgeService, LambdaService
from src.modules.agent.services.cloudwatch import CloudwatchService, CwQueryParam
from src.modules.agent.services.publisher import CWLogEvent, Publisher

from .configs import (
    CW_INSIGHTS_QUERY_DURATION,
    CW_INSIGHTS_QUERY_STRING,
    CW_INSIGHTS_QUERY_TIMEOUT,
    CW_LOGS_DELIVERY_LATENCY,
)

cloudwatch_service = CloudwatchService(
    cloudwatch_log_service=CloudwatchLogService(),
    lambda_service=LambdaService(),
    ecs_service=ECSService(),
)
publisher = Publisher(EventBridgeService())


# @logger.inject_lambda_context(log_event=True)
def handler(event, context):
    """Handle the incoming event."""
    end_time = round_n_minutes(datetime.now(UTC), 5) - timedelta(seconds=CW_LOGS_DELIVERY_LATENCY)
    start_time = end_time - timedelta(seconds=CW_INSIGHTS_QUERY_DURATION)

    # list out all monitoring log groups
    log_groups = cloudwatch_service.list_monitoring_log_groups()

    # query error logs from CloudWatch Logs
    error_logs = cloudwatch_service.query_error_logs(
        CwQueryParam(
            log_group_names=log_groups,
            query_string=CW_INSIGHTS_QUERY_STRING,
            start_time=start_time,
            end_time=end_time,
            timeout=CW_INSIGHTS_QUERY_TIMEOUT,
        )
    )

    # convert error logs to a list of events
    events = [CWLogEvent(detail=log_result.model_dump_json()) for log_result in error_logs]
    if events:
        logger.debug(f"Publishing {len(events)} error log events to EventBridge")
        publisher.publish(*events)
    else:
        logger.debug("No error log events to publish")
