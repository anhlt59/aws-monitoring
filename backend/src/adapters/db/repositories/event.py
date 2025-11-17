from src.adapters.db.mappers import EventMapper
from src.adapters.db.models import EventPersistence
from src.adapters.db.repositories.base import DynamoRepository
from src.common.utils.encoding import base64_to_json
from src.domain.models.event import Event, EventQueryResult, ListEventsDTO


class EventRepository(DynamoRepository):
    model_cls = EventPersistence
    mapper = EventMapper

    def get(self, id: str) -> Event:
        model = self._get(hash_key="EVENT", range_key=id)
        return self.mapper.to_model(model)

    def list(self, dto: ListEventsDTO | None = None) -> EventQueryResult:
        if dto is None:
            dto = ListEventsDTO()

        if dto.start_date and dto.end_date:
            range_key_condition = self.model_cls.sk.between(dto.start_date, dto.end_date)
        elif dto.start_date:
            range_key_condition = self.model_cls.pk >= dto.start_date
        elif dto.end_date:
            range_key_condition = self.model_cls.pk <= dto.end_date
        else:
            range_key_condition = None

        last_evaluated_key = base64_to_json(dto.cursor) if dto.cursor else None
        scan_index_forward = "asc" == dto.direction

        result = self._query(
            hash_key="EVENT",
            range_key_condition=range_key_condition,
            last_evaluated_key=last_evaluated_key,
            scan_index_forward=scan_index_forward,
            limit=dto.limit,
        )

        return EventQueryResult(
            items=[self.mapper.to_model(item) for item in result],
            limit=dto.limit,
            cursor=result.last_evaluated_key,
        )

    def create(self, entity: Event):
        model = EventMapper.to_persistence(entity)
        self._create(model)

    def delete(self, id: str):
        self._delete(hash_key="EVENT", range_key=id)
