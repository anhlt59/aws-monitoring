import json
from datetime import UTC, datetime
from typing import Any, Dict

from src.adapters.container import container
from src.common.logger import logger


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """AWS Lambda handler for generating daily reports"""
    try:
        logger.info("Starting daily report generation")

        # Get use case from container
        use_case = container.generate_daily_report_use_case()

        # Parse report date from event (optional)
        report_date = None
        if event.get("report_date"):
            try:
                report_date = datetime.fromisoformat(event["report_date"]).replace(tzinfo=UTC)
            except ValueError:
                logger.warning(f"Invalid report_date format: {event['report_date']}")

        # Generate report
        report_data = use_case.execute(report_date=report_date)

        logger.info(
            f"Daily report generated successfully for "
            f"{report_data['report_date']} with "
            f"{report_data['event_summary']['total_events']} events"
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "report_date": report_data["report_date"],
                    "total_events": report_data["event_summary"]["total_events"],
                    "critical_events": report_data["event_summary"]["critical_events"],
                }
            ),
        }

    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)}),
        }
