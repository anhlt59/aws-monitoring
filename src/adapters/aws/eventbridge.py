from datetime import UTC, datetime
from typing import Iterable

import boto3
from pydantic import BaseModel, Field
from types_boto3_events.client import EventBridgeClient

from src.common.configs import AWS_ENDPOINT, AWS_REGION
from src.common.logger import logger
from src.common.meta import SingletonMeta


# Models ------------------------------------
class EventsRequestEntry(BaseModel):
    Source: str
    DetailType: str | None = None
    Detail: str
    EventBusName: str = "default"
    Resources: list[str] = []
    Time: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EventBridgeService(metaclass=SingletonMeta):
    client: EventBridgeClient

    def __init__(self):
        self.client = boto3.client("events", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

    def publish_event(self, events: Iterable[EventsRequestEntry]):
        """Publish an event to the AWS EventBus."""
        response = self.client.put_events(Entries=[event.model_dump() for event in events])

        if (
            response.get("FailedEntryCount", 0) > 0
            or response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200
            or not response.get("Entries")
        ):
            raise Exception(f"Failed to publish event: {response.get('Entries')}")

        logger.debug(f"Event published successfully: {response.get('Entries')}")
