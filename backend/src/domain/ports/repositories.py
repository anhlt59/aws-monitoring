from typing import Protocol

from src.domain.models import Event, EventQueryResult
from src.domain.models.event import ListEventsDTO


class IEventRepository(Protocol):
    def get(self, id: str) -> Event: ...

    def list(self, dto: ListEventsDTO | None = None) -> EventQueryResult: ...

    def create(self, entity: Event) -> None: ...

    def delete(self, id: str) -> None: ...
