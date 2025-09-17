import json
from typing import Any, Dict

from src.adapters.container import container
from src.common.logger import Logger
from src.domain.master.dtos.event_dtos import CreateEventDTO

logger = Logger(__name__)


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """AWS Lambda handler for processing monitoring events"""
    try:
        logger.info(f"Processing {len(event.get('Records', []))} event records")

        # Get use case from container
        use_case = container.resolve("handle_monitoring_event_use_case")

        processed_count = 0
        failed_count = 0

        # Process each record
        for record in event.get("Records", []):
            try:
                # Parse event data from SQS/EventBridge record
                event_data = _parse_event_record(record)

                # Create DTO
                event_dto = CreateEventDTO(**event_data)

                # Execute use case
                processed_event = await use_case.execute(event_dto)

                logger.debug(f"Processed event {processed_event.id} with severity {processed_event.severity.name}")
                processed_count += 1

            except Exception as e:
                logger.error(f"Failed to process record: {e}")
                logger.error(f"Record data: {json.dumps(record, default=str)}")
                failed_count += 1
                continue

        logger.info(f"Processing complete: {processed_count} success, {failed_count} failed")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "processed": processed_count,
                    "failed": failed_count,
                }
            ),
        }

    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)}),
        }


def _parse_event_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Parse event data from SQS/EventBridge record"""
    try:
        # Handle SQS records
        if "body" in record:
            body = json.loads(record["body"])
            # EventBridge message in SQS
            if "Message" in body:
                event_data = json.loads(body["Message"])
            else:
                event_data = body
        # Handle direct EventBridge records
        elif "detail" in record:
            event_data = record
        else:
            raise ValueError("Unknown record format")

        # Extract required fields
        return {
            "id": event_data.get("id", record.get("messageId", "unknown")),
            "account": event_data.get("account", ""),
            "region": event_data.get("region", ""),
            "source": event_data.get("source", ""),
            "detail": event_data.get("detail", {}),
            "detail_type": event_data.get("detail-type", ""),
            "resources": event_data.get("resources", []),
        }

    except Exception as e:
        logger.error(f"Failed to parse event record: {e}")
        raise ValueError(f"Invalid event record format: {e}")
