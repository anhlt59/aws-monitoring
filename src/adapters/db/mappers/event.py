import json

from src.adapters.db.models.event import EventPersistence
from src.models.monitoring_event import Event

from .base import BaseMapper


class EventMapper(BaseMapper):
    @classmethod
    def to_persistence(cls, model: Event) -> EventPersistence:
        return EventPersistence(
            pk="EVENT",
            sk=f"{model.created_at}{model.id}",  # combine creation time and ID for sorting
            account=model.account,
            source=model.source,
            detail=json.dumps(model.detail),
            assigned=model.assigned,
            status=model.status,
            published_at=model.published_at,
            expired_at=model.created_at + 7776000,  # 3 months after creation
        )

    @classmethod
    def to_entity(cls, persistence: EventPersistence) -> Event:
        return Event(
            id=persistence.sk[10:],  # Extract the ID from the sort key
            account=persistence.account,
            source=persistence.source,
            detail=json.loads(persistence.detail),
            assigned=persistence.assigned,
            status=persistence.status,
            published_at=persistence.published_at,
        )
