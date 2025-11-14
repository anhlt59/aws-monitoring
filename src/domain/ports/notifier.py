from typing import Protocol

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.domain.models import Event


class IEventNotifier(Protocol):
    async def notify(self, event: EventBridgeEvent) -> None: ...


class IReportNotifier(Protocol):
    async def report(self, events: list[Event]) -> None: ...
