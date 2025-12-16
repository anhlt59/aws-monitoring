from src.adapters.db.repositories import EventRepository

from ..exceptions import (
    EventNotFoundError,
)


class EventUseCases:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    def get_event(self, event_id: str):
        event = self.event_repository.get(event_id)
        if not event:
            raise EventNotFoundError(f"Event with ID {event_id} not found.")
        return event

    def create_event(self, event_data: dict):
        try:
            event = self.event_repository.create(event_data)
            return event
        except Exception as e:
            raise InvalidCredentialsError(f"Failed to create event: {str(e)}")

    def list_events(self, filters: dict):
        events = self.event_repository.all(filters)
        return events

    def delete_event(self, event_id: str):
        try:
            self.event_repository.delete(event_id)
        except Exception as e:
            raise InvalidCredentialsError(f"Failed to delete event: {str(e)}")
