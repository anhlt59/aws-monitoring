import json

from src.adapters.db.models import EventPersistence
from src.domain.models import Event


class EventMapper:
    @classmethod
    def to_persistence(cls, model: Event) -> EventPersistence:
        return EventPersistence(
            # Keys
            pk="EVENT",
            sk=model.id,
            # Attributes
            id=model.id,
            account=model.account,
            region=model.region,
            source=model.source,
            detail_type=model.detail_type,
            detail=json.dumps(model.detail),
            severity=model.severity,
            resources=json.dumps(model.resources),
            published_at=model.published_at,
            updated_at=model.updated_at,
            expired_at=model.expired_at,
            # GSI1 keys
            gsi1pk=f"SOURCE#{model.source}",
            gsi1sk=f"EVENT#{model.id}",
        )

    @classmethod
    def to_entity(cls, persistence: EventPersistence) -> Event:
        return Event(
            id=persistence.id,
            account=persistence.account,
            region=persistence.region,
            source=persistence.source,
            detail_type=persistence.detail_type,
            detail=json.loads(persistence.detail),
            severity=persistence.severity,
            resources=json.loads(persistence.resources),
            published_at=persistence.published_at,
            updated_at=persistence.updated_at,
            expired_at=persistence.expired_at,
        )
