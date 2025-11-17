from src.adapters.aws import EventBridgeService
from src.domain.models.messages import Message


class Publisher:
    """Publisher adapter that publishes domain messages to EventBridge.

    Maps domain Message models to EventBridge event entry format.
    """

    def __init__(self, client: EventBridgeService) -> None:
        self.client = client

    def publish(self, messages: list[Message]) -> None:
        """Publish domain messages to EventBridge.

        Args:
            messages: List of domain Message models to publish
        """
        entries = [
            {
                "Source": message.source,
                "DetailType": message.detail_type,
                "Detail": message.detail,
                "Resources": message.resources,
                "Time": message.time,
            }
            for message in messages
        ]
        self.client.put_events(entries)
