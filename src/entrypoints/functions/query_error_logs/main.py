import os
from datetime import UTC, datetime, timedelta

from src.adapters.aws import CloudwatchLogService, ECSService, EventBridgeService, LambdaService
from src.adapters.logs import LogService
from src.adapters.publisher import Publisher
from src.common.logger import logger
from src.common.utils.datetime_utils import round_n_minutes
from src.domain.use_cases.query_error_logs import QueryParam, query_error_logs_use_case

# Constants
CW_INSIGHTS_QUERY_STRING = os.getenv(
    "CW_INSIGHTS_QUERY_STRING",
    "fields @message, @log, @logStream | filter @message like /(?i)(error|fail|exception)/ | sort @timestamp desc | limit 200",
)
CW_INSIGHTS_QUERY_DURATION = int(os.getenv("CW_INSIGHTS_QUERY_DURATION", 300))  # seconds
CW_LOGS_DELIVERY_LATENCY = int(os.getenv("CW_LOGS_DELIVERY_LATENCY", 15))  # seconds
CW_INSIGHTS_QUERY_TIMEOUT = int(os.getenv("CW_INSIGHTS_QUERY_TIMEOUT", 15))  # seconds
CW_LOG_GROUPS_CHUNK_SIZE = int(os.getenv("CW_LOG_GROUPS_CHUNK_SIZE", 10))  # limit for log groups per query

log_service = LogService(
    cloudwatch_log_service=CloudwatchLogService(),
    lambda_service=LambdaService(),
    ecs_service=ECSService(),
)
publisher = Publisher(client=EventBridgeService())


# @logger.inject_lambda_context(log_event=True)
def handler(event, context):
    try:
        end_time = round_n_minutes(datetime.now(UTC), 5) - timedelta(seconds=CW_LOGS_DELIVERY_LATENCY)
        start_time = end_time - timedelta(seconds=CW_INSIGHTS_QUERY_DURATION)
        query = QueryParam(
            query_string=CW_INSIGHTS_QUERY_STRING,
            start_time=start_time,
            end_time=end_time,
            timeout=CW_INSIGHTS_QUERY_TIMEOUT,
            chunk_size=CW_LOG_GROUPS_CHUNK_SIZE,
        )
        query_error_logs_use_case(query, log_service, publisher)
    except Exception as e:
        logger.error(f"Error occurred while querying error logs: {e}")
