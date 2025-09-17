import json
from datetime import UTC, datetime
from typing import Any, Dict, Optional

from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.value_objects.severity import Severity


class EventMapper:
    """Mapper for converting between MonitoringEvent domain entity and DynamoDB items"""

    @staticmethod
    def to_dynamodb_item(event: MonitoringEvent) -> Dict[str, Any]:
        """Convert domain entity to DynamoDB item"""
        return {
            # DynamoDB keys
            "pk": "EVENT",
            "sk": f"EVENT#{int(event.published_at.timestamp())}-{event.id}",
            # Event data
            "account": event.account,
            "region": event.region,
            "source": event.source,
            "detail": json.dumps(event.detail) if event.detail else "{}",
            "detail_type": event.detail_type,
            "severity": int(event.severity.value),
            "resources": event.resources,
            "published_at": int(event.published_at.timestamp()),
            "updated_at": int(event.updated_at.timestamp()) if event.updated_at else None,
            # TTL: 90 days from creation
            "expired_at": int(event.published_at.timestamp()) + (90 * 24 * 60 * 60),
        }

    @staticmethod
    def to_domain_entity(item: Dict[str, Any]) -> MonitoringEvent:
        """Convert DynamoDB item to domain entity"""
        # Extract event ID from sort key
        event_id = item["sk"].split("-", 1)[1] if "-" in item["sk"] else item["sk"]

        # Parse detail JSON
        detail = {}
        if item.get("detail"):
            try:
                detail = json.loads(item["detail"])
            except json.JSONDecodeError:
                detail = {"raw": item["detail"]}

        # Convert timestamps
        published_at = datetime.fromtimestamp(item["published_at"], tz=UTC)
        updated_at = None
        if item.get("updated_at"):
            updated_at = datetime.fromtimestamp(item["updated_at"], tz=UTC)

        # Convert severity
        severity = Severity(item.get("severity", 0))

        return MonitoringEvent(
            id=event_id,
            account=item["account"],
            region=item["region"],
            source=item["source"],
            detail=detail,
            detail_type=item["detail_type"],
            severity=severity,
            resources=item.get("resources", []),
            published_at=published_at,
            updated_at=updated_at,
        )

    @staticmethod
    def create_time_range_key(timestamp: datetime, event_id: str) -> str:
        """Create sort key for time-based queries"""
        return f"EVENT#{int(timestamp.timestamp())}-{event_id}"

    @staticmethod
    def extract_timestamp_from_key(sort_key: str) -> Optional[datetime]:
        """Extract timestamp from sort key"""
        try:
            # Format: EVENT#{timestamp}-{event_id}
            parts = sort_key.split("#", 1)[1].split("-", 1)
            timestamp = int(parts[0])
            return datetime.fromtimestamp(timestamp, tz=UTC)
        except (IndexError, ValueError):
            return None
