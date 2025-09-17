from datetime import datetime
from typing import List, Optional

from src.adapters.secondary.persistence.dynamodb.base_repository import BaseDynamoDBRepository
from src.adapters.secondary.persistence.mappers.event_mapper import EventMapper
from src.common.logger import logger
from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.ports.event_repository import EventRepository
from src.domain.master.value_objects.severity import Severity




class DynamoDBEventRepository(BaseDynamoDBRepository, EventRepository):
    """DynamoDB implementation of EventRepository port"""

    def __init__(self, table_name: Optional[str] = None):
        super().__init__(table_name)
        self.mapper = EventMapper()

    async def save(self, event: MonitoringEvent) -> None:
        """Save an event to DynamoDB"""
        try:
            item = self.mapper.to_dynamodb_item(event)
            await self._put_item(item)
            logger.debug(f"Event saved: {event.id}")
        except Exception as e:
            logger.error(f"Failed to save event {event.id}: {e}")
            raise

    async def find_by_id(self, event_id: str) -> Optional[MonitoringEvent]:
        """Find an event by its ID (requires scanning since ID is part of sort key)"""
        try:
            # Since event ID is embedded in sort key, we need to query with pattern
            # This is not optimal - in production, consider adding GSI with event ID
            items = await self._query(
                key_condition_expression="pk = :pk",
                expression_attribute_values={":pk": "EVENT"},
                limit=1000,  # Limit scan scope
            )

            # Filter by event ID
            for item in items:
                if item["sk"].endswith(f"-{event_id}"):
                    return self.mapper.to_domain_entity(item)

            return None

        except Exception as e:
            logger.error(f"Failed to find event {event_id}: {e}")
            raise

    async def find_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: Optional[int] = None,
    ) -> List[MonitoringEvent]:
        """Find events within a time range"""
        try:
            start_key = f"EVENT#{int(start_time.timestamp())}"
            end_key = f"EVENT#{int(end_time.timestamp())}"

            items = await self._query(
                key_condition_expression="pk = :pk AND sk BETWEEN :start_key AND :end_key",
                expression_attribute_values={
                    ":pk": "EVENT",
                    ":start_key": start_key,
                    ":end_key": end_key,
                },
                limit=limit,
                scan_index_forward=False,  # Most recent first
            )

            events = [self.mapper.to_domain_entity(item) for item in items]
            logger.debug(f"Found {len(events)} events in time range")
            return events

        except Exception as e:
            logger.error(f"Failed to find events in time range: {e}")
            raise

    async def find_by_account(self, account: str, limit: Optional[int] = None) -> List[MonitoringEvent]:
        """Find events by account"""
        try:
            items = await self._query(
                key_condition_expression="pk = :pk",
                expression_attribute_values={":pk": "EVENT"},
                limit=limit,
                scan_index_forward=False,
            )

            # Filter by account (would be better with GSI in production)
            events = []
            for item in items:
                if item.get("account") == account:
                    events.append(self.mapper.to_domain_entity(item))

            logger.debug(f"Found {len(events)} events for account {account}")
            return events

        except Exception as e:
            logger.error(f"Failed to find events for account {account}: {e}")
            raise

    async def find_critical_events(self, since: datetime, limit: Optional[int] = None) -> List[MonitoringEvent]:
        """Find critical events since a given time"""
        try:
            since_key = f"EVENT#{int(since.timestamp())}"

            items = await self._query(
                key_condition_expression="pk = :pk AND sk >= :since_key",
                expression_attribute_values={":pk": "EVENT", ":since_key": since_key},
                limit=limit,
                scan_index_forward=False,
            )

            # Filter by critical severity
            critical_events = []
            for item in items:
                severity = Severity(item.get("severity", 0))
                if severity.is_critical():
                    critical_events.append(self.mapper.to_domain_entity(item))

            logger.debug(f"Found {len(critical_events)} critical events since {since}")
            return critical_events

        except Exception as e:
            logger.error(f"Failed to find critical events: {e}")
            raise

    async def count_by_time_range(self, start_time: datetime, end_time: datetime) -> int:
        """Count events within a time range"""
        try:
            start_key = f"EVENT#{int(start_time.timestamp())}"
            end_key = f"EVENT#{int(end_time.timestamp())}"

            # Use query with Select=COUNT for efficiency
            response = self.table.query(
                KeyConditionExpression="pk = :pk AND sk BETWEEN :start_key AND :end_key",
                ExpressionAttributeValues={
                    ":pk": "EVENT",
                    ":start_key": start_key,
                    ":end_key": end_key,
                },
                Select="COUNT",
            )

            count = response.get("Count", 0)
            logger.debug(f"Counted {count} events in time range")
            return count

        except Exception as e:
            logger.error(f"Failed to count events in time range: {e}")
            raise

    async def delete_expired_events(self, before: datetime) -> int:
        """Delete events older than specified date"""
        try:
            before_key = f"EVENT#{int(before.timestamp())}"

            # Find items to delete
            items = await self._query(
                key_condition_expression="pk = :pk AND sk < :before_key",
                expression_attribute_values={":pk": "EVENT", ":before_key": before_key},
            )

            # Delete items in batches
            deleted_count = 0
            batch_size = 25  # DynamoDB batch limit

            for i in range(0, len(items), batch_size):
                batch = items[i : i + batch_size]
                with self.table.batch_writer() as batch_writer:
                    for item in batch:
                        batch_writer.delete_item(Key={"pk": item["pk"], "sk": item["sk"]})
                        deleted_count += 1

            logger.info(f"Deleted {deleted_count} expired events")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete expired events: {e}")
            raise
