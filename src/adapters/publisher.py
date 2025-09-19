from datetime import UTC, datetime

from pydantic import BaseModel, Field

from src.adapters.aws import EventBridgeService


class Message(BaseModel):
    source: str
    detail_type: str
    detail: str
    resources: list[str] = []
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Publisher:
    def __init__(self, client: EventBridgeService) -> None:
        self.client = client

    def publish(self, messages: list[Message]) -> None:
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
