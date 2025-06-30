import json
import os
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source

from src.adapters.aws.cloudwatch import CloudwatchLogService, StartQueryRequestTypeDef
from src.adapters.aws.eventbridge import EventBridgeService, PutEventsRequestEntryTypeDef
from src.common.logger import logger
from src.common.utils import round_n_minutes

LOG_GROUP_NAMES = os.getenv("LOG_GROUP_NAMES", "").split(",")
QUERY_STRING = os.getenv("QUERY_STRING")
QUERY_DURATION = os.getenv("QUERY_DURATION", 300)  # seconds
QUERY_DELAY = os.getenv("QUERY_DELAY", 1)  # seconds
QUERY_TIMEOUT = os.getenv("QUERY_TIMEOUT", 15)  # seconds

cloudwatch_service = CloudwatchLogService()
event_service = EventBridgeService()


def query_logs() -> dict[str, list[dict]]:
    """Query logs from CloudWatch based on the configured parameters."""
    query_time = round_n_minutes(datetime.now(UTC), 5)
    query_param = StartQueryRequestTypeDef(
        logGroupNames=LOG_GROUP_NAMES,
        queryString=QUERY_STRING,
        endTime=query_time,
        startTime=query_time - timedelta(seconds=QUERY_DURATION),
    )
    logs = cloudwatch_service.query_logs(
        query_param,
        timeout=QUERY_TIMEOUT,
        delay=QUERY_DELAY,
    )
    categorized_logs = defaultdict(list)
    for log in logs:
        log_group_name = log.log or "unknown"  # Use "unknown" if log.log is None
        categorized_logs[log_group_name].append(log.model_dump())
    return dict(categorized_logs)


def publish_event(data: dict, event_bus_name: str = "default"):
    """Publish logs as an event to the event bus."""
    event = PutEventsRequestEntryTypeDef(
        Source="monitoring.agent",
        DetailType="QueryErrorLogs",
        Detail=json.dumps(data),
        EventBusName=event_bus_name,
    )
    event_service.publish_event(event)


@logger.inject_lambda_context(log_event=True)
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    """Handle the incoming event."""
    if logs := query_logs():
        publish_event(logs)
    else:
        logger.debug("No logs found")
