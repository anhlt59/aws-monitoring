from typing import List, Unpack

import aioboto3
from types_aioboto3_events.client import EventBridgeClient
from types_boto3_events.type_defs import PutEventsRequestEntryTypeDef

from src.common.constants import AWS_ENDPOINT, AWS_REGION
from src.common.exceptions import UnprocessedError
from src.common.logger import logger
from src.common.meta import SingletonMeta


# Service -----------------------------------
class EventBridgeService(metaclass=SingletonMeta):
    def __init__(self, region=AWS_REGION, endpoint_url=AWS_ENDPOINT):
        self.region = region
        self.endpoint_url = endpoint_url
        self.session = aioboto3.Session()

    async def put_events(self, events: List[Unpack[PutEventsRequestEntryTypeDef]]):
        """Publish an event to the AWS EventBus."""
        async with self.session.client("events", region_name=self.region, endpoint_url=self.endpoint_url) as client:
            response = await client.put_events(Entries=events)

            failed_count = response.get("FailedEntryCount", 0)
            status_code = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            entries = response.get("Entries", [])

            if failed_count > 0 or status_code != 200 or not entries:
                raise UnprocessedError(
                    f"Failed to publish {failed_count}/{len(events)} events to EventBridge. "
                    f"Status: {status_code}, Response: {entries}"
                )
            logger.debug(f"Event published successfully: {entries}")
