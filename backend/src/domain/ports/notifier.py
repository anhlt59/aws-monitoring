from typing import Protocol

from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent

from src.domain.models import Event


class IEventNotifier(Protocol):
    def notify(self, event: EventBridgeEvent) -> None: ...


class IReportNotifier(Protocol):
    def report(self, events: list[Event]) -> None: ...
