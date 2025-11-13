from src.adapters.db.mappers import ContextMapper
from src.adapters.db.models import ContextPersistence
from src.adapters.db.repositories.base import DynamoRepository
from src.common.utils.encoding import base64_to_json
from src.domain.models import Context, ContextQueryResult, ListContextsDTO


class ContextRepository(DynamoRepository):
    model_cls = ContextPersistence
    mapper = ContextMapper

    def get(self, context_id: str) -> Context:
        """Get a context by its ID"""
        model = self._get(hash_key="CONTEXT", range_key=context_id)
        return self.mapper.to_model(model)

    def list(self, dto: ListContextsDTO | None = None) -> ContextQueryResult:
        """List contexts with optional filtering"""
        if dto is None:
            dto = ListContextsDTO()

        # Build range key condition for filtering by context type
        range_key_condition = None
        if dto.context_type:
            # CONTEXT#{context_type}#
            range_key_condition = self.model_cls.sk.begins_with(f"CONTEXT#{dto.context_type}#")

        last_evaluated_key = base64_to_json(dto.cursor) if dto.cursor else None
        scan_index_forward = "asc" == dto.direction

        result = self._query(
            hash_key="CONTEXT",
            range_key_condition=range_key_condition,
            last_evaluated_key=last_evaluated_key,
            scan_index_forward=scan_index_forward,
            limit=dto.limit,
        )

        return ContextQueryResult(
            items=[self.mapper.to_model(item) for item in result],
            limit=dto.limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: Context):
        """Create a new context"""
        model = self.mapper.to_persistence(entity)
        self._create(model)

    def update(self, entity: Context):
        """Update an existing context"""
        self._update(
            hash_key="CONTEXT",
            range_key=entity.persistence_id,
            attributes={
                "title": entity.title,
                "content": entity.content,
                "version": entity.version,
                "updated_at": entity.updated_at,
            },
        )

    def delete(self, context_id: str):
        """Delete a context"""
        self._delete(hash_key="CONTEXT", range_key=context_id)
