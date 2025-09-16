from src.common.exceptions import NotFoundError
from src.infra.db.mappers import AgentMapper
from src.infra.db.models import AgentPersistence
from src.infra.db.repositories.base import DynamoRepository, QueryResult
from src.modules.master.models.agent import Agent, UpdateAgentDTO

AgentQueryResult = QueryResult[Agent]


class AgentRepository(DynamoRepository):
    model_cls = AgentPersistence
    mapper = AgentMapper

    def get(self, id: str) -> Agent:
        model = self._get(hash_key="AGENT", range_key=id)
        return self.mapper.to_model(model)

    def list(self) -> AgentQueryResult:
        result = self._query(hash_key="AGENT", limit=100)
        return AgentQueryResult(items=(self.mapper.to_model(item) for item in result))

    def create(self, entity: Agent):
        model = AgentMapper.to_persistence(entity)
        self._create(model)

    def update(self, id: str, dto: UpdateAgentDTO):
        if attributes := dto.model_dump(exclude_none=True):
            self._update(
                hash_key="AGENT",
                range_key=id,
                attributes=attributes,
            )

    def delete(self, id: str):
        self._delete(hash_key="AGENT", range_key=id)

    def exists(self, id: str) -> bool:
        try:
            self._get(hash_key="AGENT", range_key=id, attributes_to_get=["pk", "sk"])
            return True
        except NotFoundError:
            return False
