from src.adapters.db.repositories import EventRepository
from src.common.exceptions import NotFoundError, ConflictError

from ..models import Event
from ..dtos import ListEventsDTO, PaginatedEventsDTO
from ..exceptions import EventNotFoundError, EventConflictError


class EventUseCases:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    def get_event(self, event_id: str) -> Event:
        try:
            return self.event_repository.get(event_id)
        except NotFoundError:
            raise EventNotFoundError(f"Event not found: {event_id}")

    def create_event(self, event: Event):
        try:
            self.event_repository.create(event)
        except ConflictError as e:
            raise EventConflictError(f"Failed to create event: {str(e)}")

    def list_events(self, dto: ListEventsDTO) -> PaginatedEventsDTO:
        filters = {
            "start_date": dto.start_date,
            "end_date": dto.end_date,
            "direction": dto.direction,
            "limit": dto.limit,
            "cursor": dto.cursor,
        }
        if dto.source:
            results = self.event_repository.list_by_source(source=dto.source, **filters)
        else:
            results = self.event_repository.all(**filters)

        return PaginatedEventsDTO(
            items=results.items,
            limit=dto.limit,
            previous=dto.next,
            next=results.cursor,
        )

