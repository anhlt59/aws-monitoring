import json
import os
from datetime import UTC, datetime, timedelta
from typing import Any, Dict

from src.adapters.secondary.aws.cloudwatch.log_reader import CloudWatchLogReader
from src.adapters.secondary.aws.eventbridge.event_publisher import EventBridgeEventPublisher
from src.application.agent.use_cases.query_error_logs import QueryErrorLogsUseCase
from src.common.logger import logger
from src.domain.agent.dtos.log_dtos import LogQueryDTO
from src.domain.agent.value_objects.log_level import LogLevel




def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """AWS Lambda handler for querying error logs from CloudWatch"""
    try:
        logger.info("Starting error log query")

        # Get account and region from environment or event
        account = os.environ.get("AWS_ACCOUNT_ID") or event.get("account", "")
        region = os.environ.get("AWS_REGION") or event.get("region", "us-east-1")

        if not account:
            raise ValueError("AWS Account ID not provided")

        # Create dependencies (not using container for agent-specific services)
        log_reader = CloudWatchLogReader()
        event_publisher = EventBridgeEventPublisher()

        # Create use case
        use_case = QueryErrorLogsUseCase(
            log_reader=log_reader,
            event_publisher=event_publisher,
        )

        # Parse query parameters
        query_dto = _create_query_dto(event)

        # Execute query
        summary = use_case.execute(
            query_dto=query_dto,
            account=account,
            region=region,
        )

        logger.info(f"Query completed: {summary.total_logs} logs found, {summary.error_count} errors published")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "account": account,
                    "region": region,
                    "summary": {
                        "total_logs": summary.total_logs,
                        "error_count": summary.error_count,
                        "warning_count": summary.warning_count,
                        "info_count": summary.info_count,
                        "debug_count": summary.debug_count,
                        "log_groups": summary.log_groups,
                        "time_range": summary.time_range,
                    },
                }
            ),
        }

    except Exception as e:
        logger.error(f"Failed to query error logs: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)}),
        }


def _create_query_dto(event: Dict[str, Any]) -> LogQueryDTO:
    """Create LogQueryDTO from event parameters"""
    # Default time range: last hour
    end_time = datetime.now(UTC)
    start_time = end_time - timedelta(hours=1)

    # Override with event parameters if provided
    if event.get("start_time"):
        try:
            start_time = datetime.fromisoformat(event["start_time"].replace("Z", "+00:00"))
        except ValueError:
            logger.warning(f"Invalid start_time format: {event['start_time']}")

    if event.get("end_time"):
        try:
            end_time = datetime.fromisoformat(event["end_time"].replace("Z", "+00:00"))
        except ValueError:
            logger.warning(f"Invalid end_time format: {event['end_time']}")

    # Get log groups from event or use defaults
    log_groups = event.get("log_groups", [])
    if not log_groups:
        # Default log groups for common AWS services
        log_groups = [
            "/aws/lambda",
            "/aws/ecs",
            "/aws/apigateway",
            "/aws/rds",
        ]

    # Parse log level
    log_level = None
    if event.get("log_level"):
        try:
            log_level = LogLevel(event["log_level"].upper())
        except ValueError:
            logger.warning(f"Invalid log_level: {event['log_level']}")

    return LogQueryDTO(
        log_groups=log_groups,
        start_time=start_time,
        end_time=end_time,
        filter_pattern=event.get("filter_pattern"),
        log_level=log_level,
        limit=event.get("limit", 100),
    )
