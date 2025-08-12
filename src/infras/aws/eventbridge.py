from datetime import UTC, datetime

import boto3
from pydantic import BaseModel, Field
from types_boto3_events.client import EventBridgeClient

from src.libs.configs import AWS_ENDPOINT, AWS_REGION
from src.libs.logger import logger
from src.libs.meta import SingletonMeta


# Models ------------------------------------
class Event(BaseModel):
    source: str
    detail_type: str
    detail: str
    resources: list[str] = []
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))


# Service -----------------------------------
class EventBridgeService(metaclass=SingletonMeta):
    client: EventBridgeClient

    def __init__(self, bus_name: str = "default"):
        self.client = boto3.client("events", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)
        self.bus_name = bus_name

    def publish(self, *events: Event):
        """Publish an event to the AWS EventBus."""
        entries = [
            {
                "Source": event.source,
                "DetailType": event.detail_type,
                "Detail": event.detail,
                "EventBusName": self.bus_name,
                "Resources": event.resources,
                "Time": event.time,
            }
            for event in events
        ]
        response = self.client.put_events(Entries=entries)

        if (
            response.get("FailedEntryCount", 0) > 0
            or response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200
            or not response.get("Entries")
        ):
            raise Exception(f"Failed to publish event: {response.get('Entries')}")
        logger.debug(f"Event published successfully: {response.get('Entries')}")
