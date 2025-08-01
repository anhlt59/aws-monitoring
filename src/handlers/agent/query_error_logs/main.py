import os
from datetime import UTC, datetime, timedelta

from src.adapters.aws.cloudwatch import CloudwatchLogService, CwQueryParam
from src.adapters.aws.eventbridge import Event, EventBridgeService
from src.common.logger import logger
from src.common.utils.datetime_utils import round_n_minutes

LOG_GROUP_NAMES = os.getenv("LOG_GROUP_NAMES", "").split(",")
QUERY_STRING = os.getenv("QUERY_STRING")
QUERY_DURATION = int(os.getenv("QUERY_DURATION", 300))  # seconds
QUERY_DELAY = os.getenv("QUERY_DELAY", 1)  # seconds
QUERY_TIMEOUT = os.getenv("QUERY_TIMEOUT", 15)  # seconds

cloudwatch_service = CloudwatchLogService()
publisher = EventBridgeService()


# @logger.inject_lambda_context(log_event=True)
def handler(event, context):
    """Handle the incoming event."""
    end_time = round_n_minutes(datetime.now(UTC), 5)
    start_time = end_time - timedelta(seconds=QUERY_DURATION)
    results = cloudwatch_service.query_logs(
        CwQueryParam(
            log_group_names=LOG_GROUP_NAMES,
            query_string=QUERY_STRING,
            end_time=int(end_time.timestamp()),
            start_time=int(start_time.timestamp()),
            timeout=QUERY_TIMEOUT,
            delay=QUERY_DELAY,
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
