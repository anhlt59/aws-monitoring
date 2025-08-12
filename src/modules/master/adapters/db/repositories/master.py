from src.adapters.db.mappers import MasterMapper
from src.adapters.db.models import MasterPersistence
from src.adapters.db.repositories.base import DynamoRepository, QueryResult
from src.libs.exceptions import NotFoundError
from src.models.master import Master, UpdateMasterDTO

MasterQueryResult = QueryResult[Master]


class MasterRepository(DynamoRepository):
    model_cls = MasterPersistence
    mapper = MasterMapper

    def get(self, id: str) -> Master:
        model = self._get(hash_key="MASTER", range_key=id)
        return self.mapper.to_model(model)

    def list(self) -> MasterQueryResult:
        result = self._query(hash_key="MASTER")
        return MasterQueryResult(items=(self.mapper.to_model(item) for item in result))

    def create(self, entity: Master):
        model = MasterMapper.to_persistence(entity)
        self._create(model)

    def update(self, id: str, dto: UpdateMasterDTO):
        if attributes := dto.model_dump(exclude_none=True):
            self._update(
                hash_key="MASTER",
                range_key=id,
                attributes=attributes,
            )

    def delete(self, id: str):
        self._delete(hash_key="MASTER", range_key=id)

    def exists(self, id: str) -> bool:
        try:
            self._get(hash_key="MASTER", range_key=id, attributes_to_get=["pk", "sk"])
            return True
        except NotFoundError:
            return False
