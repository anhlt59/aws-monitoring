from datetime import UTC, datetime

from pydantic import BaseModel, Field

from src.infras.aws.eventbridge import EventBridgeService


# Models ------------------------------------
class Event(BaseModel):
    source: str
    detail_type: str
    detail: str
    resources: list[str] = []
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CWLogEvent(Event):
    source: str = "monitoring.agent.logs"
    detail_type: str = "Error Log Query"


# Services ----------------------------------
class Publisher:
    def __init__(self, client: EventBridgeService):
        self.client = client

    def publish(self, *events: Event):
        entries = [
            {
                "Source": event.source,
                "DetailType": event.detail_type,
                "Detail": event.detail,
                "Resources": event.resources,
                "Time": event.time,
            }
            for event in events
        ]
        self.client.put_events(*entries)
