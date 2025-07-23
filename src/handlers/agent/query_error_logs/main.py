import os
from datetime import UTC, datetime, timedelta

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source

from src.adapters.aws.cloudwatch import CloudwatchLogService, CwQueryParam
from src.adapters.aws.eventbridge import EventBridgeService, EventsRequestEntry
from src.common.logger import logger
from src.common.utils.datetime_utils import round_n_minutes

LOG_GROUP_NAMES = os.getenv("LOG_GROUP_NAMES", "").split(",")
QUERY_STRING = os.getenv("QUERY_STRING")
QUERY_DURATION = os.getenv("QUERY_DURATION", 300)  # seconds
QUERY_DELAY = os.getenv("QUERY_DELAY", 1)  # seconds
QUERY_TIMEOUT = os.getenv("QUERY_TIMEOUT", 15)  # seconds

cloudwatch_service = CloudwatchLogService()
event_service = EventBridgeService()


# @logger.inject_lambda_context(log_event=True)
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    """Handle the incoming event."""
    end_time = round_n_minutes(datetime.now(UTC), 5)
    start_time = end_time - timedelta(seconds=QUERY_DURATION)
    logs = cloudwatch_service.query_logs(
        CwQueryParam(
            logGroupNames=LOG_GROUP_NAMES,
            queryString=QUERY_STRING,
            endTime=int(end_time.timestamp()),
            startTime=int(start_time.timestamp()),
            timeout=QUERY_TIMEOUT,
            delay=QUERY_DELAY,
        )
    )
    logger.debug(f"Found {len(logs)} logs matching the query")

    if logs:
        event_entries = (
            EventsRequestEntry(
                Source="monitoring.agent",
                DetailType="Query Error Logs",
                Detail=item.model_dump_json(),
            )
            for item in logs
        )
        event_service.publish_events(event_entries)
