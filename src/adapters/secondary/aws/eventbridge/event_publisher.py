import json
import os
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

from src.common.logger import logger
from src.domain.agent.entities.log_entry import LogEntry
from src.domain.agent.ports.event_publisher import EventPublisher as AgentEventPublisher
from src.domain.master.entities.event import MonitoringEvent
from src.domain.master.ports.event_publisher import EventPublisher as MasterEventPublisher




class EventBridgeEventPublisher(MasterEventPublisher, AgentEventPublisher):
    """EventBridge implementation of EventPublisher ports for both master and agent"""

    def __init__(self, event_bus_name: str = None):
        self.client = boto3.client("events")
        self.event_bus_name = event_bus_name or os.environ.get("EVENT_BUS_NAME", "default")

    # Master EventPublisher implementation
    async def publish_event(self, event: MonitoringEvent) -> None:
        """Publish a monitoring event to EventBridge"""
        try:
            # Convert domain event to EventBridge format
            eventbridge_event = {
                "Source": "monitoring.master",
                "DetailType": "Monitoring Event",
                "Detail": json.dumps(
                    {
                        "id": event.id,
                        "account": event.account,
                        "region": event.region,
                        "source": event.source,
                        "detail": event.detail,
                        "detail_type": event.detail_type,
                        "severity": event.severity.name,
                        "resources": event.resources,
                        "published_at": event.published_at.isoformat(),
                        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
                    }
                ),
                "Resources": event.resources,
            }

            await self._put_event(eventbridge_event)
            logger.debug(f"Published monitoring event: {event.id}")

        except Exception as e:
            logger.error(f"Failed to publish monitoring event {event.id}: {e}")
            raise

    async def publish_raw_event(
        self,
        source: str,
        detail_type: str,
        detail: Dict[str, Any],
        resources: list[str] = None,
    ) -> None:
        """Publish raw event data to EventBridge"""
        try:
            eventbridge_event = {
                "Source": source,
                "DetailType": detail_type,
                "Detail": json.dumps(detail),
                "Resources": resources or [],
            }

            await self._put_event(eventbridge_event)
            logger.debug(f"Published raw event: {source}/{detail_type}")

        except Exception as e:
            logger.error(f"Failed to publish raw event {source}/{detail_type}: {e}")
            raise

    # Agent EventPublisher implementation
    async def publish_log_event(self, log_entry: LogEntry, additional_metadata: Dict[str, Any] = None) -> None:
        """Publish a log entry as a monitoring event"""
        try:
            # Convert log entry to monitoring event format
            detail = {
                "log_entry": {
                    "timestamp": log_entry.timestamp.isoformat(),
                    "level": log_entry.level.value,
                    "message": log_entry.message,
                    "source": log_entry.source,
                    "log_group": log_entry.log_group,
                    "log_stream": log_entry.log_stream,
                    "metadata": log_entry.metadata,
                }
            }

            # Add additional metadata if provided
            if additional_metadata:
                detail.update(additional_metadata)

            eventbridge_event = {
                "Source": "monitoring.agent",
                "DetailType": "Log Error Event",
                "Detail": json.dumps(detail),
                "Resources": [log_entry.log_group] if log_entry.log_group else [],
            }

            await self._put_event(eventbridge_event)
            logger.debug(f"Published log event from {log_entry.log_group}")

        except Exception as e:
            logger.error(f"Failed to publish log event: {e}")
            raise

    async def publish_batch_log_events(
        self, log_entries: List[LogEntry], additional_metadata: Dict[str, Any] = None
    ) -> None:
        """Publish multiple log entries as monitoring events"""
        try:
            # Create batch of EventBridge events
            eventbridge_events = []

            for log_entry in log_entries:
                detail = {
                    "log_entry": {
                        "timestamp": log_entry.timestamp.isoformat(),
                        "level": log_entry.level.value,
                        "message": log_entry.message,
                        "source": log_entry.source,
                        "log_group": log_entry.log_group,
                        "log_stream": log_entry.log_stream,
                        "metadata": log_entry.metadata,
                    }
                }

                if additional_metadata:
                    detail.update(additional_metadata)

                eventbridge_events.append(
                    {
                        "Source": "monitoring.agent",
                        "DetailType": "Log Error Event",
                        "Detail": json.dumps(detail),
                        "Resources": [log_entry.log_group] if log_entry.log_group else [],
                    }
                )

            # Publish in batches (EventBridge limit is 10 events per request)
            batch_size = 10
            for i in range(0, len(eventbridge_events), batch_size):
                batch = eventbridge_events[i : i + batch_size]
                await self._put_events_batch(batch)

            logger.info(f"Published batch of {len(log_entries)} log events")

        except Exception as e:
            logger.error(f"Failed to publish batch log events: {e}")
            raise

    async def publish_agent_heartbeat(
        self, account: str, region: str, status: str, metadata: Dict[str, Any] = None
    ) -> None:
        """Publish agent heartbeat event"""
        try:
            detail = {
                "account": account,
                "region": region,
                "status": status,
                "timestamp": self._current_timestamp(),
            }

            if metadata:
                detail["metadata"] = metadata

            eventbridge_event = {
                "Source": "monitoring.agent",
                "DetailType": "Agent Heartbeat",
                "Detail": json.dumps(detail),
                "Resources": [f"arn:aws:monitoring:agent:{region}:{account}"],
            }

            await self._put_event(eventbridge_event)
            logger.debug(f"Published agent heartbeat for {account}")

        except Exception as e:
            logger.error(f"Failed to publish agent heartbeat for {account}: {e}")
            raise

    # Helper methods
    async def _put_event(self, event: Dict[str, Any]) -> None:
        """Put single event to EventBridge"""
        try:
            event["EventBusName"] = self.event_bus_name

            response = self.client.put_events(Entries=[event])

            # Check for failures
            if response.get("FailedEntryCount", 0) > 0:
                failures = response.get("Entries", [])
                failed_entries = [entry for entry in failures if entry.get("ErrorCode")]
                raise Exception(f"EventBridge put_events failed: {failed_entries}")

        except ClientError as e:
            logger.error(f"EventBridge ClientError: {e}")
            raise
        except Exception as e:
            logger.error(f"EventBridge put_event error: {e}")
            raise

    async def _put_events_batch(self, events: List[Dict[str, Any]]) -> None:
        """Put batch of events to EventBridge"""
        try:
            # Add event bus name to all events
            for event in events:
                event["EventBusName"] = self.event_bus_name

            response = self.client.put_events(Entries=events)

            # Check for failures
            if response.get("FailedEntryCount", 0) > 0:
                failures = response.get("Entries", [])
                failed_entries = [entry for entry in failures if entry.get("ErrorCode")]
                raise Exception(f"EventBridge batch put_events failed: {failed_entries}")

            logger.debug(f"Successfully published {len(events)} events to EventBridge")

        except ClientError as e:
            logger.error(f"EventBridge batch ClientError: {e}")
            raise
        except Exception as e:
            logger.error(f"EventBridge batch put_events error: {e}")
            raise

    def _current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat()
