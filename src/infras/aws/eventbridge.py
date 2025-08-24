import boto3
from types_boto3_events.client import EventBridgeClient
from types_boto3_events.type_defs import PutEventsRequestEntryTypeDef

from src.common.configs import AWS_ENDPOINT, AWS_REGION
from src.common.logger import logger
from src.common.meta import SingletonMeta


# Service -----------------------------------
class EventBridgeService(metaclass=SingletonMeta):
    client: EventBridgeClient

    def __init__(self, bus_name: str = "default"):
        self.client = boto3.client("events", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)
        self.bus_name = bus_name

    def put_events(self, *events: PutEventsRequestEntryTypeDef):
        """Publish an event to the AWS EventBus."""
        response = self.client.put_events(Entries=events)

        if (
            response.get("FailedEntryCount", 0) > 0
            or response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200
            or not response.get("Entries")
        ):
            raise Exception(f"Failed to publish event: {response.get('Entries')}")
        logger.debug(f"Event published successfully: {response.get('Entries')}")
