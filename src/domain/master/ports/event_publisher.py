from typing import Any, Dict, Protocol

from ..entities.event import MonitoringEvent


class EventPublisher(Protocol):
    """Port for publishing events to external systems"""

    async def publish_event(self, event: MonitoringEvent) -> None:
        """Publish a monitoring event to event bus"""
        ...

    async def publish_raw_event(
        self, source: str, detail_type: str, detail: Dict[str, Any], resources: list[str] = None
    ) -> None:
        """Publish raw event data to event bus"""
        ...
