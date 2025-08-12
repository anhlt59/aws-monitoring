from datetime import UTC, datetime, timedelta

from src.infras.aws import CloudwatchLogService, ECSService, LambdaService
from src.infras.aws.eventbridge import Event
from src.libs.logger import logger
from src.libs.utils.datetime_utils import round_n_minutes
from src.modules.agent.adapters import CloudwatchService, MonitoringPublisher

from .configs import (
    CW_INSIGHTS_QUERY_DURATION,
    CW_INSIGHTS_QUERY_STRING,
    CW_LOGS_DELIVERY_LATENCY,
)

cloudwatch_service = CloudwatchService(
    cloudwatch_log_service=CloudwatchLogService(),
    lambda_service=LambdaService(),
    ecs_service=ECSService(),
)
publisher = MonitoringPublisher()


# @logger.inject_lambda_context(log_event=True)
def handler(event, context):
    """Handle the incoming event."""
    end_time = round_n_minutes(datetime.now(UTC), 5) - timedelta(seconds=CW_LOGS_DELIVERY_LATENCY)
    start_time = end_time - timedelta(seconds=CW_INSIGHTS_QUERY_DURATION)

    # list out all monitoring log groups
    log_groups = cloudwatch_service.list_monitoring_log_groups()

    # query error logs from CloudWatch Logs
    error_logs = cloudwatch_service.query_error_logs(
        log_groups=log_groups,
        query_string=CW_INSIGHTS_QUERY_STRING,
        start_time=start_time,
        end_time=end_time,
    )

    # convert error logs to a list of events
    events = [
        Event(
            source="monitoring.agent.logs",
            detail_type="Query Error Logs",
            detail=log_result.model_dump_json(),
        )
        for log_result in error_logs
    ]
    logger.debug(f"Publishing {len(events)} error log events to EventBridge")
    publisher.publish(*events)
