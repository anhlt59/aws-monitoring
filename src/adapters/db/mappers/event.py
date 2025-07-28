import json

from src.adapters.db.models import EventPersistence
from src.common.configs import AWS_DYNAMODB_TTL
from src.models import Event

from .base import BaseMapper


class EventMapper(BaseMapper):
    @classmethod
    def to_persistence(cls, model: Event) -> EventPersistence:
        return EventPersistence(
            # Keys
            pk="EVENT",
            sk=model.persistence_id,  # combine creation time and ID for sorting
            gsi1sk=model.account,
            gsi1pk=model.published_at,
            # Attributes
            id=model.id,
            account=model.account,
            region=model.region,
            source=model.source,
            detail=json.dumps(model.detail),
            detail_type=model.detail_type,
            resources=model.resources,
            assigned=model.assigned,
            status=model.status,
            published_at=model.published_at,
            updated_at=model.updated_at,
            expired_at=model.published_at + AWS_DYNAMODB_TTL,
        )

    @classmethod
    def to_model(cls, persistence: EventPersistence) -> Event:
        return Event(
            id=persistence.id,
            account=persistence.account,
            source=persistence.source,
            detail=json.loads(persistence.detail),
            assigned=persistence.assigned,
            status=persistence.status,
            published_at=persistence.published_at,
            updated_at=persistence.updated_at,
        )
