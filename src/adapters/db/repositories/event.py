from src.adapters.db.mappers import EventMapper
from src.adapters.db.models import EventPersistence
from src.adapters.db.repositories.base import DynamoRepository, QueryResult
from src.models.monitoring_event import Event, ListEventsDTO, UpdateEventDTO

EventQueryResult = QueryResult[Event]


class EventRepository(DynamoRepository):
    model_cls = EventPersistence
    mapper = EventMapper

    def get(self, id: str) -> Event:
        model = self._get(hash_key="EVENT", range_key=id)
        return self.mapper.to_entity(model)

    def list(self, dto: ListEventsDTO) -> EventQueryResult:
        if dto.start_date and dto.end_date:
            range_key_condition = self.model_cls.sk.between(dto.start_date, dto.end_date)
        elif dto.start_date:
            range_key_condition = self.model_cls.pk >= dto.start_date
        elif dto.end_date:
            range_key_condition = self.model_cls.pk <= dto.end_date
        else:
            range_key_condition = None
        result = self._query(
            hash_key="EVENT",
            range_key_condition=range_key_condition,
            last_evaluated_key=dto.cursor,
            scan_index_forward="asc" == dto.direction,
            limit=dto.limit,
        )
        return EventQueryResult(
            items=[self.mapper.to_entity(project) for project in result],
            limit=dto.limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: Event):
        model = EventMapper.to_persistence(entity)
        self._create(model)

    def update(self, event_id: str, dto: UpdateEventDTO):
        attributes = dto.model_dump(exclude_none=True)
        self._update(
            hash_key="EVENT",
            range_key=event_id,
            attributes=attributes,
        )

    def delete(self, event_id: str):
        self._delete(hash_key="EVENT", range_key=event_id)
