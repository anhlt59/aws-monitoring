from src.adapters.db.mappers import EventMapper
from src.adapters.db.models import EventPersistence
from src.adapters.db.repositories.base import DynamoRepository, QueryResult
from src.models.event import Event, Status

EventQueryResult = QueryResult[Event]


class EventRepository(DynamoRepository):
    model_cls = EventPersistence
    mapper = EventMapper

    def get(self, id: str) -> Event:
        model = self._get(hash_key="EVENT", range_key=id)
        return self.mapper.to_entity(model)

    def list(
        self,
        start_date: int | None = None,
        end_date: int | None = None,
        limit: int = 50,
        direction: str = "asc",
        cursor: dict | None = None,
    ) -> EventQueryResult:
        if start_date and end_date:
            range_key_condition = self.model_cls.sk.between(start_date, end_date)
        elif start_date:
            range_key_condition = self.model_cls.pk >= start_date
        elif end_date:
            range_key_condition = self.model_cls.pk <= end_date
        else:
            range_key_condition = None
        result = self._query(
            hash_key="EVENT",
            range_key_condition=range_key_condition,
            last_evaluated_key=cursor,
            scan_index_forward="asc" == direction,
            limit=limit,
        )
        return EventQueryResult(
            items=[self.mapper.to_entity(project) for project in result],
            limit=limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: Event):
        model = EventMapper.to_persistence(entity)
        self._create(model)

    def assign_member(self, event_id: str, member: str):
        self._update(
            hash_key="EVENT",
            range_key=event_id,
            attributes={"assigned": member},
        )

    def update_status(self, event_id: str, status: Status):
        self._update(
            hash_key="EVENT",
            range_key=event_id,
            attributes={"status": status.value},
        )
