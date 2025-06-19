import json

from src.adapters.db.models.event import EventPersistence
from src.models.event import Event

from .base import BaseMapper


class EventMapper(BaseMapper):
    @classmethod
    def to_persistence(cls, model: Event) -> EventPersistence:
        return EventPersistence(
            pk="EVENT",
            sk=model.id,
            project=model.project,
            source=model.source,
            detail=json.dumps(model.detail),
            assigned=model.assigned,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_entity(cls, persistence: EventPersistence) -> Event:
        return Event(
            id=persistence.sk,
            project=persistence.project,
            source=persistence.source,
            detail=json.loads(persistence.detail),
            assigned=persistence.assigned,
            status=persistence.status,
            created_at=persistence.created_at,
            updated_at=persistence.updated_at,
        )
