from src.adapters.db.mappers import EventMapper
from src.adapters.db.models import EventPersistence
from src.common.utils.encoding import base64_to_json
from src.domain.monitoring.models.event import Event

from .base import DynamoRepository, QueryResult

EventQueryResult = QueryResult[Event]


class EventRepository(DynamoRepository):
    model_cls = EventPersistence
    mapper = EventMapper

    def get(self, id: str) -> Event:
        model = self._get(hash_key="EVENT", range_key=id)
        return self.mapper.to_entity(model)

    def all(
        self,
        start_date: int | None = None,
        end_date: int | None = None,
        direction: str = "desc",
        limit: int = 50,
        cursor: str | None = None,
    ) -> EventQueryResult:
        """List all events with optional time range filtering."""

        if start_date and end_date:
            range_key_condition = self.model_cls.sk.between(f"EVENT#{start_date}", f"EVENT#{end_date}")
        elif start_date:
            range_key_condition = self.model_cls.sk >= f"EVENT#{start_date}"
        elif end_date:
            range_key_condition = self.model_cls.sk <= f"EVENT#{end_date}"
        else:
            range_key_condition = None

        last_evaluated_key = base64_to_json(cursor) if cursor else None
        scan_index_forward = "asc" == direction

        result = self._query(
            hash_key="EVENT",
            range_key_condition=range_key_condition,
            last_evaluated_key=last_evaluated_key,
            scan_index_forward=scan_index_forward,
            limit=limit,
        )

        return EventQueryResult(
            items=[self.mapper.to_entity(item) for item in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def list_by_source(
        self,
        source: str,
        start_date: int | None = None,
        end_date: int | None = None,
        direction: str = "desc",
        limit: int = 50,
        cursor: str | None = None,
    ) -> EventQueryResult:
        """List events by source with optional time range."""
        if start_date and end_date:
            range_key_condition = self.model_cls.gsi1sk.between(f"EVENT#{start_date}", f"EVENT#{end_date}")
        elif start_date:
            range_key_condition = self.model_cls.gsi1sk >= f"EVENT#{start_date}"
        elif end_date:
            range_key_condition = self.model_cls.gsi1sk <= f"EVENT#{end_date}"
        else:
            range_key_condition = None

        last_evaluated_key = base64_to_json(cursor) if cursor else None
        scan_index_forward = "asc" == direction

        result = self._query(
            hash_key=f"SOURCE#{source}",
            range_key_condition=range_key_condition,
            index=self.model_cls.gsi1,
            last_evaluated_key=last_evaluated_key,
            scan_index_forward=scan_index_forward,
            limit=limit,
        )

        return EventQueryResult(
            items=[self.mapper.to_entity(item) for item in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: Event):
        model = EventMapper.to_persistence(entity)
        self._create(model)

    def delete(self, id: str):
        self._delete(hash_key="EVENT", range_key=id)
