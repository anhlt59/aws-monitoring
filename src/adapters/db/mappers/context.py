import json

from src.adapters.db.models import ContextPersistence
from src.domain.models import Context


class ContextMapper:
    @classmethod
    def to_persistence(cls, model: Context) -> ContextPersistence:
        return ContextPersistence(
            # Keys
            pk="CONTEXT",
            sk=model.persistence_id,
            # Attributes
            context_type=model.context_type,
            title=model.title,
            content=json.dumps(model.content),
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_model(cls, persistence: ContextPersistence) -> Context:
        # Extract ID from sk: CONTEXT#{context_type}#{id}
        parts = persistence.sk.split("#", 2)
        context_id = parts[2] if len(parts) > 2 else persistence.sk

        return Context(
            id=context_id,
            context_type=persistence.context_type,
            title=persistence.title,
            content=json.loads(persistence.content),
            version=persistence.version,
            created_at=persistence.created_at,
            updated_at=persistence.updated_at,
        )
